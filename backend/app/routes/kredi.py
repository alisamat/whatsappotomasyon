"""
KREDİ — KuveytTürk 3D Secure ödeme + abonelik yönetimi
"""
import uuid
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, KrediSatinAlma, FaturaBilgisi, FaturaKaydi

logger = logging.getLogger(__name__)
bp = Blueprint('kredi', __name__, url_prefix='/api/kredi')

# ── PAKET TANIMI ──────────────────────────────────────────────────────────────
PAKETLER = [
    # Aylık abonelikler
    {
        'id': 'aylik_baslangic', 'turu': 'aylik', 'ad': 'Aylık Başlangıç',
        'kredi': 30,   'fiyat_tl': 199,  'gun': 31,
        'aciklama': 'Ayda ~6 yer gösterme belgesi',
    },
    {
        'id': 'aylik_pro', 'turu': 'aylik', 'ad': 'Aylık Pro',
        'kredi': 100,  'fiyat_tl': 499,  'gun': 31,
        'aciklama': 'Ayda ~20 yer gösterme belgesi', 'popular': True,
    },
    # Yıllık abonelik
    {
        'id': 'yillik_pro', 'turu': 'yillik', 'ad': 'Yıllık Pro',
        'kredi': 1500, 'fiyat_tl': 3990, 'gun': 365,
        'aciklama': 'Yılda ~300 belge · %33 tasarruf', 'indirim': True,
    },
    # Ekstra kredi (sadece aktif abonelere)
    {
        'id': 'ekstra_20', 'turu': 'ekstra', 'ad': 'Ekstra 20 Kredi',
        'kredi': 20,   'fiyat_tl': 149,  'gun': 0,
        'aciklama': '4 yer gösterme belgesi · Süre uzatmaz',
    },
    {
        'id': 'ekstra_50', 'turu': 'ekstra', 'ad': 'Ekstra 50 Kredi',
        'kredi': 50,   'fiyat_tl': 299,  'gun': 0,
        'aciklama': '10 yer gösterme belgesi · Süre uzatmaz',
    },
]

PAKET_MAP = {p['id']: p for p in PAKETLER}


def _abonelik_aktif_mi(user: User) -> bool:
    return bool(user.paket_bitis and user.paket_bitis > datetime.utcnow())


# ── ENDPOINTS ─────────────────────────────────────────────────────────────────

@bp.route('/paketler', methods=['GET'])
def paketler():
    return jsonify({'success': True, 'paketler': PAKETLER})


@bp.route('/bakiye', methods=['GET'])
@jwt_required()
def bakiye():
    user = User.query.get(int(get_jwt_identity()))
    return jsonify({'success': True, 'kredi': user.kredi if user else 0})


@bp.route('/paket-durum', methods=['GET'])
@jwt_required()
def paket_durum():
    """Abonelik + kredi durumunu döndür."""
    user = User.query.get(int(get_jwt_identity()))
    aktif = _abonelik_aktif_mi(user)
    kalan_gun = None
    if aktif and user.paket_bitis:
        kalan_gun = max(0, (user.paket_bitis - datetime.utcnow()).days)
    return jsonify({
        'success': True,
        'aktif': aktif,
        'kredi': user.kredi,
        'paket_bitis': user.paket_bitis.strftime('%d.%m.%Y') if user.paket_bitis else None,
        'kalan_gun': kalan_gun,
    })


@bp.route('/satin-al', methods=['POST'])
@jwt_required()
def satin_al():
    """3D Secure ödeme başlat."""
    from app.services.kuveytturk_payment import start_3d_secure_payment
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı.'}), 404

    d = request.get_json() or {}
    paket_id = d.get('paket_id')
    paket = PAKET_MAP.get(paket_id)
    if not paket:
        return jsonify({'success': False, 'message': 'Geçersiz paket.'}), 400

    # Ekstra kredi sadece aktif abonelere
    if paket['turu'] == 'ekstra' and not _abonelik_aktif_mi(user):
        return jsonify({'success': False,
                        'message': 'Ekstra kredi sadece aktif abonelik sahibine satılır.'}), 403

    card_holder_name  = d.get('kart_sahibi', '').strip()
    card_number       = d.get('kart_no', '').replace(' ', '')
    card_expire_month = d.get('son_ay', '')
    card_expire_year  = d.get('son_yil', '')
    card_cvv          = d.get('cvv', '')

    if not all([card_holder_name, card_number, card_expire_month, card_expire_year, card_cvv]):
        return jsonify({'success': False, 'message': 'Kart bilgileri eksik.'}), 400

    order_id     = str(uuid.uuid4()).replace('-', '')[:20]
    amount_kurus = str(int(paket['fiyat_tl'] * 100))

    kayit = KrediSatinAlma(
        user_id=user.id,
        paket_adi=paket['ad'],
        paket_turu=paket['turu'],
        gecerlilik_gun=paket['gun'],
        kredi_miktari=paket['kredi'],
        tutar_tl=paket['fiyat_tl'],
        odeme_durumu='bekliyor',
        iyzico_token=order_id,
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

    return jsonify({'success': True, 'html_content': result['html_content'], 'order_id': order_id})


@bp.route('/callback', methods=['POST'])
def callback():
    """KuveytTürk 3D Secure callback."""
    from app.services.kuveytturk_payment import verify_3d_callback, provision_payment
    auth_response = request.form.get('AuthenticationResponse', '')
    if not auth_response:
        return _redirect_fail('Geçersiz callback.')

    verified = verify_3d_callback(auth_response)
    if not verified['success']:
        _odeme_guncelle(verified.get('order_id'), 'iptal')
        return _redirect_fail(verified.get('error', 'Doğrulama başarısız.'))

    order_id = verified['order_id']
    amount   = verified['amount']
    md       = verified['md']

    provision = provision_payment(order_id, amount, md)
    if not provision['success']:
        _odeme_guncelle(order_id, 'iptal')
        return _redirect_fail(provision.get('error', 'Ödeme alınamadı.'))

    kayit = KrediSatinAlma.query.filter_by(iyzico_token=order_id, odeme_durumu='bekliyor').first()
    if kayit:
        user = User.query.get(kayit.user_id)
        if user:
            user.kredi += kayit.kredi_miktari
            # Abonelik tarihini güncelle (ekstra kredi hariç)
            if kayit.gecerlilik_gun and kayit.gecerlilik_gun > 0:
                now = datetime.utcnow()
                baz = (max(now, user.paket_bitis)
                       if user.paket_bitis and user.paket_bitis > now else now)
                user.paket_bitis = baz + timedelta(days=kayit.gecerlilik_gun)

        kayit.odeme_durumu = 'onaylandi'

        # Fatura oluştur
        try:
            fatura_no = f'WA-{datetime.utcnow().strftime("%Y%m%d")}-{kayit.user_id}-{kayit.id}'
            db.session.add(FaturaKaydi(
                user_id=kayit.user_id,
                fatura_no=fatura_no,
                paket_adi=kayit.paket_adi,
                kredi_miktari=kayit.kredi_miktari,
                tutar_tl=kayit.tutar_tl,
                durum='odendi',
            ))
        except Exception as e:
            logger.warning(f'[Kredi] Fatura oluşturulamadı: {e}')

        db.session.commit()
        logger.info(f'✅ Ödeme başarılı — {order_id}, {kayit.kredi_miktari} kredi')

    frontend_url = current_app.config.get('FRONTEND_URL', 'https://whatsappotomasyon.com.tr')
    return redirect(f'{frontend_url}/kredi?odeme=basarili')


# ── FATURA BİLGİSİ ────────────────────────────────────────────────────────────

@bp.route('/fatura-bilgisi', methods=['GET'])
@jwt_required()
def fatura_bilgisi_al():
    user = User.query.get(int(get_jwt_identity()))
    fb = FaturaBilgisi.query.filter_by(user_id=user.id).first()
    return jsonify({'success': True, 'fatura_bilgisi': fb.to_dict() if fb else {}})


@bp.route('/fatura-bilgisi', methods=['PUT'])
@jwt_required()
def fatura_bilgisi_kaydet():
    user = User.query.get(int(get_jwt_identity()))
    d = request.get_json() or {}
    fb = FaturaBilgisi.query.filter_by(user_id=user.id).first()
    if not fb:
        fb = FaturaBilgisi(user_id=user.id)
        db.session.add(fb)
    fb.sirket_ad     = d.get('sirket_ad', fb.sirket_ad)
    fb.vergi_no      = d.get('vergi_no', fb.vergi_no)
    fb.vergi_dairesi = d.get('vergi_dairesi', fb.vergi_dairesi)
    fb.il            = d.get('il', fb.il)
    fb.adres         = d.get('adres', fb.adres)
    fb.eposta        = d.get('eposta', fb.eposta)
    fb.telefon       = d.get('telefon', fb.telefon)
    fb.guncelleme    = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'fatura_bilgisi': fb.to_dict()})


@bp.route('/faturalar', methods=['GET'])
@jwt_required()
def faturalar():
    user = User.query.get(int(get_jwt_identity()))
    kayitlar = (FaturaKaydi.query
                .filter_by(user_id=user.id)
                .order_by(FaturaKaydi.tarih.desc())
                .limit(50).all())
    return jsonify({'success': True, 'faturalar': [f.to_dict() for f in kayitlar]})


# ── YARDIMCILAR ───────────────────────────────────────────────────────────────

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
