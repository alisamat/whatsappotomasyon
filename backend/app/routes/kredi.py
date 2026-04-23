"""
KREDİ — KuveytTürk 3D Secure ödeme entegrasyonu
"""
import uuid
import logging
from flask import Blueprint, request, jsonify, redirect, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, KrediSatinAlma
from app.services.kuveytturk_payment import (
    start_3d_secure_payment, verify_3d_callback, provision_payment
)

logger = logging.getLogger(__name__)
bp = Blueprint('kredi', __name__, url_prefix='/api/kredi')

PAKETLER = [
    {'id': 'p10',  'kredi': 10,  'fiyat_tl': 29,  'ad': 'Başlangıç'},
    {'id': 'p25',  'kredi': 25,  'fiyat_tl': 59,  'ad': 'Standart'},
    {'id': 'p60',  'kredi': 60,  'fiyat_tl': 119, 'ad': 'Ekonomik'},
    {'id': 'p150', 'kredi': 150, 'fiyat_tl': 249, 'ad': 'Pro'},
]

def _paket_bul(paket_id=None, kredi=None):
    for p in PAKETLER:
        if paket_id and p['id'] == paket_id:
            return p
        if kredi and p['kredi'] == int(kredi):
            return p
    return None


@bp.route('/paketler', methods=['GET'])
def paketler():
    return jsonify({'success': True, 'paketler': PAKETLER})


@bp.route('/bakiye', methods=['GET'])
@jwt_required()
def bakiye():
    user = User.query.get(int(get_jwt_identity()))
    return jsonify({'success': True, 'kredi': user.kredi if user else 0})


@bp.route('/satin-al', methods=['POST'])
@jwt_required()
def satin_al():
    """3D Secure ödeme başlat — HTML döndür."""
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı.'}), 404

    d = request.get_json() or {}

    # Frontend { kredi, fiyat } veya { paket_id } gönderebilir
    paket = _paket_bul(paket_id=d.get('paket_id'), kredi=d.get('kredi'))
    if not paket:
        return jsonify({'success': False, 'message': 'Geçersiz paket.'}), 400

    card_holder_name  = d.get('kart_sahibi', '').strip()
    card_number       = d.get('kart_no', '').replace(' ', '')
    card_expire_month = d.get('son_ay', '')
    card_expire_year  = d.get('son_yil', '')
    card_cvv          = d.get('cvv', '')

    if not all([card_holder_name, card_number, card_expire_month, card_expire_year, card_cvv]):
        return jsonify({'success': False, 'message': 'Kart bilgileri eksik.'}), 400

    order_id = str(uuid.uuid4()).replace('-', '')[:20]
    # Kuruş cinsinden (TL * 100)
    amount_kurus = str(paket['fiyat_tl'] * 100)

    # DB'ye pending kayıt
    kayit = KrediSatinAlma(
        user_id=user.id,
        paket_adi=paket['ad'],
        kredi_miktari=paket['kredi'],
        tutar_tl=paket['fiyat_tl'],
        odeme_durumu='bekliyor',
        iyzico_token=order_id,  # order_id'yi buraya saklıyoruz
    )
    db.session.add(kayit)
    db.session.commit()

    result = start_3d_secure_payment(
        card_holder_name=card_holder_name,
        card_number=card_number,
        card_expire_month=card_expire_month,
        card_expire_year=card_expire_year,
        card_cvv=card_cvv,
        amount=amount_kurus,
        order_id=order_id,
        client_ip=request.remote_addr or '127.0.0.1',
        callback_path='/api/kredi/callback',
    )

    if not result['success']:
        kayit.odeme_durumu = 'iptal'
        db.session.commit()
        return jsonify({'success': False, 'message': result.get('error', 'Ödeme başlatılamadı.')}), 500

    return jsonify({
        'success': True,
        'html_content': result['html_content'],
        'order_id': order_id,
    })


@bp.route('/callback', methods=['POST'])
def callback():
    """KuveytTürk 3D Secure callback — Bank buraya POST atar."""
    auth_response = request.form.get('AuthenticationResponse', '')
    if not auth_response:
        logger.error('Callback: AuthenticationResponse yok')
        return _redirect_fail('Geçersiz callback.')

    verified = verify_3d_callback(auth_response)
    if not verified['success']:
        logger.error(f"Callback doğrulama başarısız: {verified.get('error')}")
        _odeme_guncelle(verified.get('order_id'), 'iptal')
        return _redirect_fail(verified.get('error', 'Doğrulama başarısız.'))

    order_id = verified['order_id']
    amount   = verified['amount']
    md       = verified['md']

    provision = provision_payment(order_id, amount, md)
    if not provision['success']:
        logger.error(f"Provision başarısız: {provision.get('error')}")
        _odeme_guncelle(order_id, 'iptal')
        return _redirect_fail(provision.get('error', 'Ödeme alınamadı.'))

    # Ödeme başarılı — kredi ekle
    kayit = KrediSatinAlma.query.filter_by(iyzico_token=order_id, odeme_durumu='bekliyor').first()
    if kayit:
        user = User.query.get(kayit.user_id)
        if user:
            user.kredi += kayit.kredi_miktari
        kayit.odeme_durumu = 'onaylandi'
        db.session.commit()
        logger.info(f"✅ Ödeme başarılı — OrderId: {order_id}, Kredi: {kayit.kredi_miktari}")

    frontend_url = current_app.config.get('FRONTEND_URL', 'https://whatsappotomasyon.com.tr')
    return redirect(f'{frontend_url}/kredi?odeme=basarili')


def _odeme_guncelle(order_id, durum):
    if not order_id:
        return
    kayit = KrediSatinAlma.query.filter_by(iyzico_token=order_id).first()
    if kayit:
        kayit.odeme_durumu = durum
        db.session.commit()


def _redirect_fail(hata):
    frontend_url = current_app.config.get('FRONTEND_URL', 'https://whatsappotomasyon.com.tr')
    from urllib.parse import quote
    return redirect(f'{frontend_url}/kredi?odeme=basarisiz&hata={quote(hata)}')
