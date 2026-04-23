"""
BELGE — Üretilen PDF'leri servis et
"""
from flask import Blueprint, Response
from app.services.belge_store import al

bp = Blueprint('belge', __name__, url_prefix='/api/belge')


@bp.route('/<token>', methods=['GET'])
def belge_indir(token):
    pdf_bytes = al(token)
    if not pdf_bytes:
        return 'Belge bulunamadı veya süresi doldu.', 404
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="belge.pdf"'},
    )
