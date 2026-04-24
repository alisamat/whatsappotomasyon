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


_TASINMAZ_PROMPT = """Aşağıdaki metinden taşınmaz/adres bilgilerini çıkar ve şu JSON'u döndür:
{{
  "sehir": "il adı",
  "ilce": "ilçe adı",
  "mahalle": "mahalle/köy adı",
  "ada": "ada no (varsa, yoksa null)",
  "parsel": "parsel no (varsa, yoksa null)",
  "adres": "tam adres metni",
  "alan_m2": sayı veya null
}}
Sadece JSON döndür.
Metin: {metin}"""


def tasinmaz_parse_et(metin: str) -> dict:
    """Serbest metinden taşınmaz bilgisi çıkar."""
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return {'adres': metin, 'sehir': '', 'ilce': '', 'mahalle': '', 'ada': None, 'parsel': None, 'alan_m2': None}
    try:
        payload = {
            'contents': [{'parts': [{'text': _TASINMAZ_PROMPT.format(metin=metin)}]}],
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
        logger.warning(f'[MetinParse] tasinmaz Gemini hatası: {e}')
        return {'adres': metin, 'sehir': '', 'ilce': '', 'mahalle': '', 'ada': None, 'parsel': None, 'alan_m2': None}


_ALICI_DETAY_PROMPT = """Aşağıdaki metinden kişi bilgilerini çıkar ve şu JSON'u döndür:
{{
  "ad_soyad": "kişinin adı soyadı",
  "tc_no": "TC kimlik numarası (11 haneli, yoksa null)",
  "telefon": "telefon numarası (yoksa null)",
  "adres": "adres (yoksa null)"
}}
Sadece JSON döndür.
Metin: {metin}"""


def alici_detay_parse_et(metin: str) -> dict:
    """İsim, TC, telefon çıkar."""
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return {'ad_soyad': metin.strip(), 'tc_no': None, 'telefon': None, 'adres': None}
    try:
        payload = {
            'contents': [{'parts': [{'text': _ALICI_DETAY_PROMPT.format(metin=metin)}]}],
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
        if not result.get('ad_soyad'):
            result['ad_soyad'] = metin.strip()
        return result
    except Exception as e:
        logger.warning(f'[MetinParse] alici_detay Gemini hatası: {e}')
        return {'ad_soyad': metin.strip(), 'tc_no': None, 'telefon': None, 'adres': None}


_YER_GOSTERME_PROMPT = """Türkçe mesajdan taşınmaz yer gösterme bilgilerini çıkar, şu JSON'u döndür:
{{
  "alici_ad": "kişinin adı soyadı veya null",
  "alici_tc": "11 haneli TC kimlik no veya null",
  "alici_tel": "telefon numarası veya null",
  "adres": "taşınmaz adresi (sokak/mah/ilçe/şehir) veya null",
  "sehir": "il adı veya null",
  "ilce": "ilçe adı veya null",
  "mahalle": "mahalle adı veya null",
  "islem_turu": "kira" veya "satis" veya null,
  "fiyat": fiyat rakamı (sadece sayı, TL/₺ işareti olmadan) veya null,
  "komisyon_ay": kira komisyonu ay sayısı veya null,
  "komisyon_yuzde": satış komisyonu yüzdesi veya null
}}
Kesin olmayan alanlar için null yaz, tahmin etme.
Sadece JSON döndür.
Metin: {metin}"""

_YER_GOSTERME_BOS = {
    'alici_ad': None, 'alici_tc': None, 'alici_tel': None,
    'adres': None, 'sehir': None, 'ilce': None, 'mahalle': None,
    'islem_turu': None, 'fiyat': None, 'komisyon_ay': None, 'komisyon_yuzde': None,
}


def yer_gosterme_parse_et(metin: str) -> dict:
    """Serbest metinden tüm yer gösterme alanlarını AI ile çıkar."""
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return _yer_gosterme_regex(metin)
    try:
        payload = {
            'contents': [{'parts': [{'text': _YER_GOSTERME_PROMPT.format(metin=metin)}]}],
            'generationConfig': {'temperature': 0.1, 'maxOutputTokens': 512},
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
        return {**_YER_GOSTERME_BOS, **result}
    except Exception as e:
        logger.warning(f'[MetinParse] yer_gosterme Gemini hatası: {e}')
        return _yer_gosterme_regex(metin)


def _yer_gosterme_regex(metin: str) -> dict:
    """Regex fallback — Gemini yoksa basit çıkarım."""
    sonuc = dict(_YER_GOSTERME_BOS)
    # Telefon
    tel_m = re.search(r'(\+?90|0)?[5][0-9]{9}', metin.replace(' ', ''))
    if tel_m:
        sonuc['alici_tel'] = tel_m.group()
    # TC (11 hane, 1 ile başlar)
    tc_m = re.search(r'\b[1-9][0-9]{10}\b', metin)
    if tc_m:
        sonuc['alici_tc'] = tc_m.group()
    # Fiyat (rakam + opsiyonel TL/₺)
    fiyat_m = re.search(r'(\d[\d.]*)\s*(?:tl|lira|₺)', metin.lower())
    if fiyat_m:
        try:
            sonuc['fiyat'] = float(fiyat_m.group(1).replace('.', '').replace(',', '.'))
        except Exception:
            pass
    # İşlem türü
    if re.search(r'kira|kiralık|kiralama', metin.lower()):
        sonuc['islem_turu'] = 'kira'
    elif re.search(r'satış|satılık|satilik|sat[ıi]ş', metin.lower()):
        sonuc['islem_turu'] = 'satis'
    return sonuc


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
