"""
EMLAK PROFİLİ — Emlakçı kişisel/işletme bilgileri
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import db, User, EmlakciProfil

bp = Blueprint('emlak_profil', __name__, url_prefix='/api/emlak-profil')


@bp.route('', methods=['GET'])
@jwt_required()
def profil_al():
    user = User.query.get(int(get_jwt_identity()))
    p = EmlakciProfil.query.filter_by(user_id=user.id).first()
    if not p:
        return jsonify({'success': True, 'profil': None})
    return jsonify({'success': True, 'profil': p.to_dict()})


@bp.route('', methods=['PUT'])
@jwt_required()
def profil_kaydet():
    user = User.query.get(int(get_jwt_identity()))
    d = request.get_json() or {}
    p = EmlakciProfil.query.filter_by(user_id=user.id).first()
    if not p:
        p = EmlakciProfil(user_id=user.id, ad_soyad=d.get('ad_soyad', user.ad_soyad))
        db.session.add(p)
    p.ad_soyad              = d.get('ad_soyad', p.ad_soyad)
    p.isletme_adi           = d.get('isletme_adi', p.isletme_adi)
    p.is_adresi             = d.get('is_adresi', p.is_adresi)
    p.telefon               = d.get('telefon', p.telefon)
    p.lisans_no             = d.get('lisans_no', p.lisans_no)
    p.vergi_dairesi         = d.get('vergi_dairesi', p.vergi_dairesi)
    p.vergi_no              = d.get('vergi_no', p.vergi_no)
    p.komisyon_kira_ay      = d.get('komisyon_kira_ay', p.komisyon_kira_ay)
    p.komisyon_satis_yuzde  = d.get('komisyon_satis_yuzde', p.komisyon_satis_yuzde)
    p.yetki_sehri           = d.get('yetki_sehri', p.yetki_sehri)
    p.guncelleme            = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'profil': p.to_dict()})
