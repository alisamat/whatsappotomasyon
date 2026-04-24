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


_YER_GOSTERME_PROMPT = """Türkçe mesajdan taşınmaz yer gösterme bilgilerini çıkar.

KURALLAR:
1. Mesajın başında telefon/TC/sayı içermeyen 2-4 Türkçe kelime varsa → alici_ad (ör: "ali okan 75000" → "Ali Okan")
2. 4-9 haneli büyük sayı → fiyat olabilir (ör: 75000, 500000, 1500000)
3. "bin" → ×1000, "milyon" → ×1000000 (ör: "15 bin" → 15000, "1.5 milyon" → 1500000)
4. kira/kiralık/kiralama → islem_turu: "kira" | satış/satılık → islem_turu: "satis"
5. "X ay" → komisyon_ay | "%X" → komisyon_yuzde
6. Kesin olmayan adres/il/ilçe/mahalle için null yaz

ÖRNEKLER:
- "ali okan 75000" → {{"alici_ad": "Ali Okan", "fiyat": 75000}}
- "kiralık 18000 komisyon 1 ay" → {{"islem_turu": "kira", "fiyat": 18000, "komisyon_ay": 1}}
- "satılık 1500000 %2" → {{"islem_turu": "satis", "fiyat": 1500000, "komisyon_yuzde": 2}}
- "Ahmet Kaya 0532... kadıköy kiralık 15000" → {{"alici_ad": "Ahmet Kaya", "alici_tel": "0532...", "ilce": "Kadıköy", "islem_turu": "kira", "fiyat": 15000}}
- "15 bin" → {{"fiyat": 15000}}
- "kira" → {{"islem_turu": "kira"}}

JSON (kesin olmayan alanlar null):
{{
  "alici_ad": string|null,
  "alici_tc": string|null,
  "alici_tel": string|null,
  "adres": string|null,
  "sehir": string|null,
  "ilce": string|null,
  "mahalle": string|null,
  "islem_turu": "kira"|"satis"|null,
  "fiyat": number|null,
  "komisyon_ay": number|null,
  "komisyon_yuzde": number|null
}}

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
    ml = metin.lower()

    # Telefon
    tel_m = re.search(r'(\+?90|0)?[5][0-9]{9}', metin.replace(' ', ''))
    if tel_m:
        sonuc['alici_tel'] = tel_m.group()

    # TC (11 hane, 1 ile başlar)
    tc_m = re.search(r'\b[1-9][0-9]{10}\b', metin)
    if tc_m:
        sonuc['alici_tc'] = tc_m.group()

    # İsim tespiti: telefon ve TC yoksa baştaki Türkçe kelimeler isim
    if not sonuc.get('alici_tel') and not sonuc.get('alici_tc'):
        kelimeler = metin.strip().split()
        isim_parts = []
        for k in kelimeler:
            temiz = re.sub(r'[^a-zA-ZğĞşŞçÇıİöÖüÜ]', '', k)
            if temiz and len(temiz) >= 2:
                isim_parts.append(k)
            else:
                break
        if 2 <= len(isim_parts) <= 3:
            sonuc['alici_ad'] = ' '.join(isim_parts).title()

    # Fiyat — "X bin" veya "X milyon" formatı
    bin_m = re.search(r'(\d+(?:[.,]\d+)?)\s*bin', ml)
    milyon_m = re.search(r'(\d+(?:[.,]\d+)?)\s*milyon', ml)
    if milyon_m:
        try:
            sonuc['fiyat'] = float(milyon_m.group(1).replace(',', '.')) * 1_000_000
        except Exception:
            pass
    elif bin_m:
        try:
            sonuc['fiyat'] = float(bin_m.group(1).replace(',', '.')) * 1_000
        except Exception:
            pass

    # Fiyat — sayı + TL/₺ etiketi
    if not sonuc.get('fiyat'):
        fiyat_m = re.search(r'(\d[\d.]*)\s*(?:tl|lira|₺)', ml)
        if fiyat_m:
            try:
                sonuc['fiyat'] = float(fiyat_m.group(1).replace('.', '').replace(',', '.'))
            except Exception:
                pass

    # Fiyat — etiketsiz 4-7 haneli sayı (TC değil)
    if not sonuc.get('fiyat'):
        for m in re.finditer(r'\b(\d{4,7})\b', metin):
            num_str = m.group(1)
            if sonuc.get('alici_tc') and num_str == sonuc['alici_tc']:
                continue
            try:
                sonuc['fiyat'] = float(num_str)
                break
            except Exception:
                pass

    # İşlem türü
    if re.search(r'kira|kiralık|kiralama', ml):
        sonuc['islem_turu'] = 'kira'
    elif re.search(r'satış|satılık|satilik|sat[ıi]ş', ml):
        sonuc['islem_turu'] = 'satis'

    # Komisyon
    kom_ay_m = re.search(r'(\d+)\s*ay', ml)
    if kom_ay_m:
        sonuc['komisyon_ay'] = int(kom_ay_m.group(1))
    kom_yuzde_m = re.search(r'%\s*(\d+(?:[.,]\d+)?)', metin)
    if kom_yuzde_m:
        try:
            sonuc['komisyon_yuzde'] = float(kom_yuzde_m.group(1).replace(',', '.'))
        except Exception:
            pass

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
