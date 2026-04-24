"""
ADMIN — Sektör numara yönetimi, kullanıcı listesi
"""
import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, SektorNumara, IslemLog

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _admin_kontrol():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    return user and user.email.endswith('@admin.com')  # basit admin kontrolü


@bp.route('/kullanicilar', methods=['GET'])
@jwt_required()
def kullanicilar():
    if not _admin_kontrol():
        return jsonify({'success': False}), 403
    users = User.query.order_by(User.kayit_tarihi.desc()).all()
    return jsonify({'success': True, 'kullanicilar': [u.to_dict() for u in users]})


@bp.route('/sektor-numaralar', methods=['GET'])
@jwt_required()
def sektor_numaralar_listele():
    if not _admin_kontrol():
        return jsonify({'success': False}), 403
    numaralar = SektorNumara.query.all()
    return jsonify({'success': True, 'numaralar': [{
        'id': n.id, 'phone_number_id': n.phone_number_id,
        'wa_no': n.wa_no, 'sektor': n.sektor,
        'aciklama': n.aciklama, 'aktif': n.aktif,
    } for n in numaralar]})


@bp.route('/sektor-numaralar', methods=['POST'])
@jwt_required()
def sektor_numara_ekle():
    if not _admin_kontrol():
        return jsonify({'success': False}), 403
    d = request.get_json() or {}
    sn = SektorNumara(
        phone_number_id=d['phone_number_id'],
        wa_no=d['wa_no'],
        sektor=d['sektor'],
        aciklama=d.get('aciklama', ''),
        access_token=d.get('access_token', ''),
    )
    db.session.add(sn)
    db.session.commit()
    return jsonify({'success': True, 'id': sn.id}), 201


@bp.route('/seed', methods=['POST'])
def seed():
    """Tek seferlik: SektorNumara kaydı ekle. SECRET_KEY ile korunuyor."""
    if request.headers.get('X-Admin-Key') != current_app.config.get('SECRET_KEY'):
        return jsonify({'success': False}), 403
    d = request.get_json() or {}
    existing = SektorNumara.query.filter_by(phone_number_id=d.get('phone_number_id')).first()
    if existing:
        return jsonify({'success': False, 'message': 'Zaten var.'}), 409
    sn = SektorNumara(
        phone_number_id=d['phone_number_id'],
        wa_no=d['wa_no'],
        sektor=d['sektor'],
        aciklama=d.get('aciklama', ''),
        access_token=d.get('access_token', ''),
        aktif=True,
    )
    db.session.add(sn)
    db.session.commit()
    return jsonify({'success': True, 'id': sn.id}), 201


@bp.route('/seed', methods=['GET'])
def seed_read():
    """SektorNumara kaydını oku (access_token dahil)."""
    if request.headers.get('X-Admin-Key') != current_app.config.get('SECRET_KEY'):
        return jsonify({'success': False}), 403
    phone_number_id = request.args.get('phone_number_id')
    if phone_number_id:
        sn = SektorNumara.query.filter_by(phone_number_id=phone_number_id).first()
        if not sn:
            return jsonify({'success': False, 'message': 'Kayıt bulunamadı.'}), 404
        return jsonify({'success': True, 'kayit': {
            'id': sn.id, 'phone_number_id': sn.phone_number_id,
            'wa_no': sn.wa_no, 'sektor': sn.sektor,
            'aciklama': sn.aciklama, 'aktif': sn.aktif,
            'access_token': sn.access_token,
        }})
    numaralar = SektorNumara.query.all()
    return jsonify({'success': True, 'kayitlar': [{
        'id': n.id, 'phone_number_id': n.phone_number_id,
        'wa_no': n.wa_no, 'sektor': n.sektor,
        'aciklama': n.aciklama, 'aktif': n.aktif,
        'access_token': n.access_token,
    } for n in numaralar]})


@bp.route('/seed', methods=['PATCH'])
def seed_update():
    """Mevcut SektorNumara kaydını güncelle (access_token vb.)."""
    if request.headers.get('X-Admin-Key') != current_app.config.get('SECRET_KEY'):
        return jsonify({'success': False}), 403
    d = request.get_json() or {}
    sn = SektorNumara.query.filter_by(phone_number_id=d.get('phone_number_id')).first()
    if not sn:
        return jsonify({'success': False, 'message': 'Kayıt bulunamadı.'}), 404
    if 'access_token' in d:
        sn.access_token = d['access_token']
    if 'wa_no' in d:
        sn.wa_no = d['wa_no']
    if 'sektor' in d:
        sn.sektor = d['sektor']
    if 'aciklama' in d:
        sn.aciklama = d['aciklama']
    if 'aktif' in d:
        sn.aktif = d['aktif']
    db.session.commit()
    return jsonify({'success': True}), 200


@bp.route('/islem-log', methods=['GET'])
@jwt_required()
def islem_log():
    if not _admin_kontrol():
        return jsonify({'success': False}), 403
    logs = IslemLog.query.order_by(IslemLog.tarih.desc()).limit(200).all()
    return jsonify({'success': True, 'islemler': [{
        'id': l.id, 'telefon': l.telefon, 'sektor': l.sektor,
        'islem_tipi': l.islem_tipi, 'durum': l.durum,
        'kredi': l.kredi_kullanim, 'tarih': l.tarih.isoformat(),
    } for l in logs]})
