"""
METİN PARSE — Serbest metinden alıcı bilgisi çıkarma (Gemini Flash)
"""
import os
import re
import json
import logging
import requests

logger = logging.getLogger(__name__)

_API_URL = (
    'https://generativelanguage.googleapis.com/v1beta/models/'
    'gemini-2.5-flash:generateContent?key={key}'
)

_PROMPT = """Aşağıdaki mesajdan alıcı kişi bilgilerini çıkar.
Varsa şu alanları JSON olarak döndür:
- "ad": kişinin adı soyadı
- "telefon": telefon numarası (varsa)
- "adres": adres (varsa)

Eğer bu mesaj bir kişi bilgisi içermiyorsa {"alici_yok": true} döndür.
Sadece JSON döndür, başka açıklama yazma.

Mesaj: {metin}"""


def alici_parse_et(metin: str) -> dict | None:
    """
    Serbest metinden alıcı bilgisi çıkar.
    Başarılıysa {'ad': ..., 'telefon': ..., 'adres': ...} döner.
    Alıcı yoksa None döner.
    """
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return _regex_parse(metin)

    try:
        payload = {
            'contents': [{'parts': [{'text': _PROMPT.format(metin=metin)}]}],
            'generationConfig': {'temperature': 0.1, 'maxOutputTokens': 256},
        }
        resp = requests.post(_API_URL.format(key=api_key), json=payload, timeout=15)
        resp.raise_for_status()
        text = (
            resp.json()
            .get('candidates', [{}])[0]
            .get('content', {})
            .get('parts', [{}])[0]
            .get('text', '')
            .strip()
        )
        if text.startswith('```'):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

        result = json.loads(text)
        if result.get('alici_yok'):
            return None
        if not result.get('ad'):
            return None
        return {
            'ad': result.get('ad', ''),
            'telefon': result.get('telefon', ''),
            'adres': result.get('adres', ''),
        }
    except Exception as e:
        logger.warning(f'[MetinParse] Gemini hatası, regex fallback: {e}')
        return _regex_parse(metin)


def _regex_parse(metin: str) -> dict | None:
    """Basit regex tabanlı fallback."""
    tel_match = re.search(r'(\+?90|0)?[5][0-9]{9}', metin.replace(' ', ''))
    if not tel_match:
        return None
    telefon = tel_match.group()
    ad = re.sub(r'(\+?90|0)?[5][0-9]{9}', '', metin).strip()
    ad = re.sub(r'[,;:|]', ' ', ad).strip()
    ad = ' '.join(ad.split())
    if len(ad) < 2:
        return None
    return {'ad': ad, 'telefon': telefon, 'adres': ''}
