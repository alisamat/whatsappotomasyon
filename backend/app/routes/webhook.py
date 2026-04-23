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
from app.services.metin_parse import alici_parse_et

logger = logging.getLogger(__name__)
bp = Blueprint('webhook', __name__, url_prefix='/api/webhook')

# Kullanıcı oturumları: {telefon: {fotograflar:[], konum:None, alici:None}}
_SESSIONS: dict[str, dict] = {}


def _session_al(telefon: str) -> dict:
    if telefon not in _SESSIONS:
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
        msg_type        = mesaj.get('type', '')

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

        # Kredi kontrol (ön kontrol)
        handler = handler_al(sektor)
        if not handler:
            logger.warning(f'[Webhook] Handler yok: {sektor}')
            return jsonify({'status': 'ok'}), 200

        # Session'a veri ekle
        session = _session_al(gonderen_no)

        if msg_type == 'image':
            media_id = mesaj.get('image', {}).get('id')
            if media_id:
                foto_bytes = wa.medya_indir(media_id, access_token)
                if foto_bytes and len(session['fotograflar']) < handler.MAX_FOTOGRAF:
                    session['fotograflar'].append(foto_bytes)
                    kalan = handler.MAX_FOTOGRAF - len(session['fotograflar'])
                    wa.mesaj_gonder(phone_number_id, access_token, gonderen_no,
                                    f'📸 Fotoğraf alındı ({len(session["fotograflar"])}/{handler.MAX_FOTOGRAF}). '
                                    + (f'{kalan} daha ekleyebilirsiniz.' if kalan > 0 else 'Maksimuma ulaştınız.'))

        elif msg_type == 'location':
            session['konum'] = wa.konum_mesaji_isle(mesaj.get('location', {}))
            wa.mesaj_gonder(phone_number_id, access_token, gonderen_no, '📍 Konum alındı.')

        elif msg_type == 'contacts':
            kisi = mesaj.get('contacts', [{}])[0]
            isim = kisi.get('name', {}).get('formatted_name', '')
            tel_list = kisi.get('phones', [{}])
            tel = tel_list[0].get('phone', '') if tel_list else ''
            session['alici'] = {'ad': isim, 'telefon': tel}
            wa.mesaj_gonder(phone_number_id, access_token, gonderen_no,
                            f'👤 Alıcı bilgisi alındı: {isim}')

        elif msg_type == 'text':
            metin = mesaj.get('text', {}).get('body', '').strip()
            metin_lower = metin.lower()
            if metin_lower in ('iptal', 'sıfırla', 'reset', 'yeni'):
                _session_temizle(gonderen_no)
                wa.mesaj_gonder(phone_number_id, access_token, gonderen_no,
                                '🔄 Oturum sıfırlandı. Yeni işlem başlatabilirsiniz.')
                return jsonify({'status': 'ok'}), 200
            elif metin_lower in ('durum', 'bakiye', 'kredi'):
                wa.mesaj_gonder(phone_number_id, access_token, gonderen_no,
                                f'💳 Kredi bakiyeniz: {user.kredi:.0f}')
                return jsonify({'status': 'ok'}), 200
            else:
                # Alıcı bilgisi metinden çıkarılmaya çalışılır
                alici = alici_parse_et(metin)
                if alici:
                    session['alici'] = alici
                    wa.mesaj_gonder(phone_number_id, access_token, gonderen_no,
                                    f'👤 Alıcı bilgisi alındı: {alici["ad"]}'
                                    + (f' ({alici["telefon"]})' if alici.get('telefon') else ''))
                else:
                    wa.mesaj_gonder(phone_number_id, access_token, gonderen_no,
                                    handler.beklenen_veri_mesaji())
                return jsonify({'status': 'ok'}), 200

        # Yeterli veri var mı? → işlemi başlat
        if handler.session_tamam_mi(session):
            if not kayit.kredi_dus(user, handler.KREDI_MALIYETI):
                kayit.kredi_yetersiz_bildir(user, handler.KREDI_MALIYETI,
                                            phone_number_id, access_token,
                                            current_app.config.get('FRONTEND_URL', ''))
            else:
                basarili = handler.handle(gonderen_no, session, phone_number_id, access_token)
                if basarili:
                    _session_temizle(gonderen_no)

    except Exception as e:
        logger.error(f'[Webhook] İşlem hatası: {e}', exc_info=True)

    return jsonify({'status': 'ok'}), 200
