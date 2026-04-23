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

_PROMPT = """Aşağıdaki mesajı analiz et ve şu JSON formatını döndür:

{{
  "tip": "alici" | "adres" | "hicbiri",
  "ad": "kişi adı soyadı (varsa)",
  "telefon": "telefon numarası (varsa)",
  "adres": "sokak/mahalle/şehir adresi (varsa)"
}}

Kurallar:
- Mesajda kişi adı veya telefon varsa → "tip": "alici"
- Mesajda sadece adres/konum bilgisi varsa (sokak, mahalle, şehir, ilçe vb.) → "tip": "adres"
- Hiçbiri yoksa → "tip": "hicbiri"
- Sadece JSON döndür, başka açıklama yazma.

Mesaj: {metin}"""


def metin_isle(metin: str) -> dict:
    """
    Serbest metni analiz eder.
    Dönüş: {'tip': 'alici'|'adres'|'hicbiri', 'ad', 'telefon', 'adres'}
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
        return json.loads(text)
    except Exception as e:
        logger.warning(f'[MetinParse] Gemini hatası, regex fallback: {e}')
        return _regex_parse(metin)


def alici_parse_et(metin: str) -> dict | None:
    """Geriye dönük uyumluluk için."""
    sonuc = metin_isle(metin)
    if sonuc.get('tip') == 'alici' and sonuc.get('ad'):
        return {'ad': sonuc['ad'], 'telefon': sonuc.get('telefon', ''), 'adres': sonuc.get('adres', '')}
    return None


def _regex_parse(metin: str) -> dict:
    """Basit regex tabanlı fallback — her zaman dict döner."""
    tel_match = re.search(r'(\+?90|0)?[5][0-9]{9}', metin.replace(' ', ''))
    if tel_match:
        telefon = tel_match.group()
        ad = re.sub(r'(\+?90|0)?[5][0-9]{9}', '', metin).strip()
        ad = re.sub(r'[,;:|]', ' ', ad).strip()
        ad = ' '.join(ad.split())
        if ad:
            return {'tip': 'alici', 'ad': ad, 'telefon': telefon, 'adres': ''}
    # Sadece isim var mı? (2+ kelime, harf, telefon yok)
    kelimeler = metin.strip().split()
    if 2 <= len(kelimeler) <= 4 and all(k.replace('ğ','').replace('ş','').replace('ç','').replace('ı','').replace('ö','').replace('ü','').isalpha() for k in kelimeler):
        return {'tip': 'alici', 'ad': metin.strip(), 'telefon': '', 'adres': ''}
    return {'tip': 'hicbiri', 'ad': '', 'telefon': '', 'adres': ''}
