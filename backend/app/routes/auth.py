"""
AUTH — Kayıt, giriş, profil
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, KayitBekleyen

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/kayit', methods=['POST'])
def kayit():
    """Yeni kullanıcı kaydı (token ile veya direkt)."""
    d = request.get_json() or {}
    token    = d.get('token')  # WhatsApp kayıt linki tokeni
    ad_soyad = d.get('ad_soyad', '').strip()
    email    = d.get('email', '').strip().lower()
    telefon  = d.get('telefon', '').strip()
    sifre    = d.get('sifre', '')
    sektor   = d.get('sektor', '')

    if not all([ad_soyad, email, telefon, sifre]):
        return jsonify({'success': False, 'message': 'Tüm alanlar zorunludur.'}), 400

    # Token varsa bekleyen kaydı doğrula
    if token:
        bekleyen = KayitBekleyen.query.filter_by(token=token, tamamlandi=False).first()
        if not bekleyen:
            return jsonify({'success': False, 'message': 'Geçersiz veya kullanılmış kayıt linki.'}), 400
        telefon = bekleyen.telefon
        sektor  = sektor or bekleyen.sektor

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Bu e-posta zaten kayıtlı.'}), 400
    if User.query.filter_by(telefon=telefon).first():
        return jsonify({'success': False, 'message': 'Bu telefon numarası zaten kayıtlı.'}), 400

    user = User(
        ad_soyad=ad_soyad,
        email=email,
        telefon=telefon,
        sifre_hash=generate_password_hash(sifre),
        sektor=sektor,
        kredi=10.0,  # hoş geldin kredisi
    )
    db.session.add(user)

    if token:
        bekleyen = KayitBekleyen.query.filter_by(token=token).first()
        if bekleyen:
            bekleyen.tamamlandi = True

    db.session.commit()
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'success': True, 'token': access_token, 'user': user.to_dict()}), 201


@bp.route('/giris', methods=['POST'])
def giris():
    d = request.get_json() or {}
    email = d.get('email', '').strip().lower()
    sifre = d.get('sifre', '')

    user = User.query.filter_by(email=email, aktif=True).first()
    if not user or not check_password_hash(user.sifre_hash, sifre):
        return jsonify({'success': False, 'message': 'E-posta veya şifre hatalı.'}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({'success': True, 'token': access_token, 'user': user.to_dict()})


@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'success': False}), 404
    return jsonify({'success': True, 'user': user.to_dict()})
