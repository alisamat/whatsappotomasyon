"""
BELGE — Üretilen PDF/PNG belgelerini servis et
"""
from flask import Blueprint, Response
from app.services.belge_store import al, mime_turu

bp = Blueprint('belge', __name__, url_prefix='/api/belge')


@bp.route('/<token>', methods=['GET'])
def belge_indir(token):
    data, uzanti = al(token)
    if not data:
        return 'Belge bulunamadı veya süresi doldu.', 404
    return Response(
        data,
        mimetype=mime_turu(uzanti),
        headers={'Content-Disposition': f'inline; filename="belge.{uzanti}"'},
    )
