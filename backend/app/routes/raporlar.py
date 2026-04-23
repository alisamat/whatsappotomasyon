"""
RAPORLAR — Yer gösterme kayıtları
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, YerGosterme

bp = Blueprint('raporlar', __name__, url_prefix='/api/raporlar')


@bp.route('/yer-gostermeler', methods=['GET'])
@jwt_required()
def liste():
    user = User.query.get(int(get_jwt_identity()))
    sayfa     = int(request.args.get('sayfa', 1))
    boyut     = min(int(request.args.get('boyut', 20)), 50)
    tur       = request.args.get('islem_turu', '')
    baslangic = request.args.get('baslangic', '')
    bitis     = request.args.get('bitis', '')

    q = YerGosterme.query.filter_by(user_id=user.id)
    if tur:
        q = q.filter_by(islem_turu=tur)
    if baslangic:
        q = q.filter(YerGosterme.olusturma >= baslangic)
    if bitis:
        q = q.filter(YerGosterme.olusturma <= bitis + ' 23:59:59')

    toplam  = q.count()
    kayitlar = q.order_by(YerGosterme.olusturma.desc()).offset((sayfa - 1) * boyut).limit(boyut).all()
    return jsonify({
        'success': True, 'toplam': toplam, 'sayfa': sayfa, 'boyut': boyut,
        'kayitlar': [k.to_dict() for k in kayitlar],
    })


@bp.route('/yer-gostermeler/<int:gosterme_id>', methods=['GET'])
@jwt_required()
def detay(gosterme_id):
    user = User.query.get(int(get_jwt_identity()))
    yg = YerGosterme.query.filter_by(id=gosterme_id, user_id=user.id).first_or_404()
    return jsonify({'success': True, 'kayit': yg.to_dict()})
