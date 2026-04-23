"""
META CLOUD API — WhatsApp mesaj gönderme istemcisi
"""
import requests
import logging

logger = logging.getLogger(__name__)

META_API_VERSION = 'v25.0'
GRAPH_URL = f'https://graph.facebook.com/{META_API_VERSION}'


def _headers(access_token: str) -> dict:
    return {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}


def mesaj_gonder(phone_number_id: str, access_token: str, alici_no: str, metin: str) -> bool:
    """Alıcıya düz metin mesaj gönder."""
    url = f'{GRAPH_URL}/{phone_number_id}/messages'
    payload = {
        'messaging_product': 'whatsapp',
        'to': alici_no,
        'type': 'text',
        'text': {'body': metin},
    }
    try:
        r = requests.post(url, json=payload, headers=_headers(access_token), timeout=15)
        r.raise_for_status()
        return True
    except Exception as e:
        logger.error(f'[WA] Mesaj gönderilemedi {alici_no}: {e}')
        return False


def belge_gonder(phone_number_id: str, access_token: str, alici_no: str,
                 dosya_url: str, dosya_adi: str, aciklama: str = '') -> bool:
    """PDF/belge gönder (hosted URL üzerinden)."""
    url = f'{GRAPH_URL}/{phone_number_id}/messages'
    payload = {
        'messaging_product': 'whatsapp',
        'to': alici_no,
        'type': 'document',
        'document': {
            'link': dosya_url,
            'filename': dosya_adi,
            'caption': aciklama,
        },
    }
    try:
        r = requests.post(url, json=payload, headers=_headers(access_token), timeout=15)
        r.raise_for_status()
        return True
    except Exception as e:
        logger.error(f'[WA] Belge gönderilemedi {alici_no}: {e}')
        return False


def medya_indir(media_id: str, access_token: str) -> bytes | None:
    """Meta media_id'den ham bayt indir."""
    try:
        # 1) media URL al
        r = requests.get(f'{GRAPH_URL}/{media_id}', headers=_headers(access_token), timeout=15)
        r.raise_for_status()
        media_url = r.json().get('url')
        if not media_url:
            return None
        # 2) dosyayı indir
        r2 = requests.get(media_url, headers=_headers(access_token), timeout=30)
        r2.raise_for_status()
        return r2.content
    except Exception as e:
        logger.error(f'[WA] Medya indirilemedi {media_id}: {e}')
        return None


def konum_mesaji_isle(location: dict) -> dict:
    """Gelen konum objesini normalize et."""
    return {
        'lat': location.get('latitude'),
        'lng': location.get('longitude'),
        'ad': location.get('name', ''),
        'adres': location.get('address', ''),
        'google_maps': f"https://maps.google.com/?q={location.get('latitude')},{location.get('longitude')}",
    }
