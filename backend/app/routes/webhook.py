"""
WHATSAPP WEBHOOK
GET  /api/webhook  — Meta doğrulama
POST /api/webhook  — Gelen mesajlar
"""
import logging
from flask import Blueprint, request, jsonify, current_app
from app.models import db, SektorNumara
from app.services import whatsapp_client as wa
from app.services import kayit_akisi as kayit
from app.services.sektorler import handler_al

logger = logging.getLogger(__name__)
bp = Blueprint('webhook', __name__, url_prefix='/api/webhook')

# Kullanıcı oturumları: {telefon: session_dict}
_SESSIONS: dict[str, dict] = {}


def _session_al(telefon: str, sektor: str) -> dict:
    if telefon not in _SESSIONS:
        if sektor == 'emlak':
            from app.services.sektorler.emlak import yeni_session
            _SESSIONS[telefon] = yeni_session()
        else:
            _SESSIONS[telefon] = {'fotograflar': [], 'konum': None, 'alici': None}
    return _SESSIONS[telefon]


def _session_temizle(telefon: str):
    _SESSIONS.pop(telefon, None)


# ── GET: Meta webhook doğrulama ────────────────────────────────────────────────
@bp.route('', methods=['GET'])
def verify():
    mode      = request.args.get('hub.mode')
    token     = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    verify_token = current_app.config.get('META_WEBHOOK_VERIFY_TOKEN', '')
    if mode == 'subscribe' and token == verify_token:
        logger.info('[Webhook] Doğrulama başarılı')
        return challenge, 200
    return 'Forbidden', 403


# ── POST: Gelen mesaj ──────────────────────────────────────────────────────────
@bp.route('', methods=['POST'])
def gelen_mesaj():
    data = request.get_json(silent=True) or {}
    try:
        entry    = data.get('entry', [{}])[0]
        changes  = entry.get('changes', [{}])[0]
        value    = changes.get('value', {})
        messages = value.get('messages', [])
        if not messages:
            return jsonify({'status': 'ok'}), 200

        phone_number_id = value.get('metadata', {}).get('phone_number_id', '')
        mesaj           = messages[0]
        gonderen_no     = mesaj.get('from', '')

        # Sektör + access_token bul
        sn = SektorNumara.query.filter_by(phone_number_id=phone_number_id, aktif=True).first()
        if not sn:
            logger.warning(f'[Webhook] Tanımsız phone_number_id: {phone_number_id}')
            return jsonify({'status': 'ok'}), 200

        sektor       = sn.sektor
        access_token = sn.access_token

        # Kullanıcı kayıtlı mı?
        user = kayit.kayitli_mi(gonderen_no)
        if not user:
            kayit.kayit_linki_gonder(gonderen_no, sektor, phone_number_id, access_token,
                                     current_app.config.get('FRONTEND_URL', ''))
            return jsonify({'status': 'ok'}), 200

        # Handler al
        handler = handler_al(sektor)
        if not handler:
            logger.warning(f'[Webhook] Handler yok: {sektor}')
            return jsonify({'status': 'ok'}), 200

        # Session
        session = _session_al(gonderen_no, sektor)

        # State machine — tüm mesaj işleme handler içinde
        tamamlandi = handler.mesaj_isle(
            gonderen_no, mesaj, session,
            phone_number_id, access_token, user
        )
        if tamamlandi:
            _session_temizle(gonderen_no)

    except Exception as e:
        logger.error(f'[Webhook] İşlem hatası: {e}', exc_info=True)

    return jsonify({'status': 'ok'}), 200
