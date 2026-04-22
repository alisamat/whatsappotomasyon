"""
KREDİ — Satın alma ve bakiye
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, KrediSatinAlma
import iyzipay, json, uuid

bp = Blueprint('kredi', __name__, url_prefix='/api/kredi')

PAKETLER = {
    'baslangic': {'ad': 'Başlangıç',  'kredi': 50,  'fiyat': 49.90},
    'standart':  {'ad': 'Standart',   'kredi': 150, 'fiyat': 129.90},
    'profesyonel':{'ad': 'Profesyonel','kredi': 400, 'fiyat': 299.90},
}


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
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı.'}), 404

    d = request.get_json() or {}
    paket_id = d.get('paket_id')
    paket = PAKETLER.get(paket_id)
    if not paket:
        return jsonify({'success': False, 'message': 'Geçersiz paket.'}), 400

    options = {
        'api_key':    current_app.config['IYZICO_API_KEY'],
        'secret_key': current_app.config['IYZICO_SECRET_KEY'],
        'base_url':   current_app.config['IYZICO_BASE_URL'],
    }
    request_data = {
        'locale': 'tr',
        'conversationId': str(uuid.uuid4()),
        'price': str(paket['fiyat']),
        'paidPrice': str(paket['fiyat']),
        'currency': 'TRY',
        'installment': '1',
        'paymentChannel': 'WEB',
        'paymentGroup': 'PRODUCT',
        'paymentCard': d.get('kart', {}),
        'buyer': {
            'id': str(user.id),
            'name': user.ad_soyad.split()[0] if user.ad_soyad else 'Ad',
            'surname': user.ad_soyad.split()[-1] if user.ad_soyad else 'Soyad',
            'email': user.email,
            'identityNumber': '11111111111',
            'registrationAddress': 'Türkiye',
            'city': 'Istanbul',
            'country': 'Turkey',
            'ip': request.remote_addr or '127.0.0.1',
        },
        'shippingAddress': {'contactName': user.ad_soyad, 'city': 'Istanbul', 'country': 'Turkey', 'address': 'Türkiye'},
        'billingAddress':  {'contactName': user.ad_soyad, 'city': 'Istanbul', 'country': 'Turkey', 'address': 'Türkiye'},
        'basketItems': [{
            'id': paket_id,
            'name': paket['ad'],
            'category1': 'Kredi',
            'itemType': 'VIRTUAL',
            'price': str(paket['fiyat']),
        }],
    }
    try:
        result = iyzipay.Payment().create(request_data, options)
        result_json = json.loads(result.read().decode('utf-8'))
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    if result_json.get('status') == 'success':
        user.kredi += paket['kredi']
        kayit = KrediSatinAlma(
            user_id=user.id,
            paket_adi=paket['ad'],
            kredi_miktari=paket['kredi'],
            tutar_tl=paket['fiyat'],
            odeme_durumu='onaylandi',
        )
        db.session.add(kayit)
        db.session.commit()
        return jsonify({'success': True, 'kredi': user.kredi, 'message': f"{paket['kredi']} kredi eklendi."})
    else:
        return jsonify({'success': False, 'message': result_json.get('errorMessage', 'Ödeme hatası.')}), 400
