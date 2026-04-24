"""
EMLAK PROFİLİ — Emlakçı kişisel/işletme bilgileri
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import db, User, EmlakciProfil

bp = Blueprint('emlak_profil', __name__, url_prefix='/api/emlak-profil')

_ALANLAR = [
    'ad_soyad', 'isletme_adi', 'is_adresi', 'telefon', 'eposta',
    'ttyb_no', 'lisans_no', 'oda_adi', 'oda_sicil_no', 'ticaret_sicil_no',
    'vergi_dairesi', 'vergi_no', 'yetki_sehri',
    'slogan', 'web_sitesi', 'instagram', 'facebook', 'logo_base64',
    'komisyon_kira_ay', 'komisyon_satis_yuzde', 'belge_format',
]


@bp.route('', methods=['GET'])
@jwt_required()
def profil_al():
    user = User.query.get(int(get_jwt_identity()))
    p = EmlakciProfil.query.filter_by(user_id=user.id).first()
    return jsonify({'success': True, 'profil': p.to_dict() if p else None})


@bp.route('', methods=['PUT'])
@jwt_required()
def profil_kaydet():
    user = User.query.get(int(get_jwt_identity()))
    d = request.get_json() or {}
    p = EmlakciProfil.query.filter_by(user_id=user.id).first()
    if not p:
        p = EmlakciProfil(user_id=user.id, ad_soyad=d.get('ad_soyad', user.ad_soyad))
        db.session.add(p)
    for alan in _ALANLAR:
        if alan in d:
            setattr(p, alan, d[alan])
    p.guncelleme = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'profil': p.to_dict()})
