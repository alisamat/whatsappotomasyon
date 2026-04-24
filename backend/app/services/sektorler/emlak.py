"""
EMLAK SEKTÖRÜ — Yer Gösterme Sözleşmesi
Sadeleştirilmiş 3-adım akış: hosgeldin → veri_toplama → onay_bekleniyor
"""
import re
import difflib
import logging
from datetime import date, datetime, timedelta
from app.services.sektorler.base import BaseSektorHandler
from app.services import whatsapp_client as wa

logger = logging.getLogger(__name__)

SESSION_TTL_DAKIKA = 30  # Bu süre içinde mesaj gelmezse session sıfırlanır


def _eslesir(ml: str, komutlar) -> bool:
    """
    Yazım hatası toleranslı komut eşleştirme.
    - Exact match
    - Tekrar harf normalleştirme: "kapatt" → "kapat", "evett" → "evet"
    - Fuzzy match (tek kelime, ≥4 karakter): "kapt" → "kapat", "kaat" → "kapat"
    """
    if not ml:
        return False
    komut_listesi = list(komutlar)
    if ml in komutlar:
        return True
    if len(ml) <= 2:          # Çok kısa: sadece exact match
        return False
    # Tekrarlanan harfleri temizle: "kapatt" → "kapat"
    norm = re.sub(r'(.)\1+', r'\1', ml)
    if norm in komutlar:
        return True
    # Tek kelimeli, makul uzunlukta → fuzzy
    if ' ' not in ml and 3 <= len(ml) <= 15:
        esik = 0.72 if len(ml) <= 5 else 0.78   # Kısa kelimeler için daha toleranslı
        if difflib.get_close_matches(ml, komut_listesi, n=1, cutoff=esik):
            return True
        if norm != ml and difflib.get_close_matches(norm, komut_listesi, n=1, cutoff=esik):
            return True
    return False


def yeni_session() -> dict:
    return {
        'adim': 'hosgeldin',
        'son_mesaj': datetime.utcnow().isoformat(),
        'sablon_no': 1,
        'fotograflar': [],
        'konum': None,
        'alici': {'ad_soyad': None, 'tc_no': None, 'telefon': None, 'adres': None},
        'tasinmaz': {'sehir': None, 'ilce': None, 'mahalle': None, 'ada': None,
                     'parsel': None, 'adres': None, 'alan_m2': None},
        'islem_turu': None,
        'fiyat': None,
        'komisyon_kira_ay': None,
        'komisyon_satis_yuzde': None,
    }


class EmlakHandler(BaseSektorHandler):
    SEKTOR_KODU    = 'emlak'
    KREDI_MALIYETI = 5
    MIN_FOTOGRAF   = 0
    MAX_FOTOGRAF   = 4

    def session_tamam_mi(self, session: dict) -> bool:
        return bool(
            session.get('alici', {}).get('ad_soyad') and
            (session.get('tasinmaz', {}).get('adres') or session.get('konum')) and
            session.get('islem_turu') and
            session.get('fiyat')
        )

    def beklenen_veri_mesaji(self) -> str:
        return self._hosgeldin_metni()

    def handle(self, *args, **kwargs) -> bool:
        return False

    def mesaj_isle(self, telefon, mesaj, session, phone_number_id, access_token, user):
        adim     = session.get('adim', 'hosgeldin')
        msg_type = mesaj.get('type', '')
        metin    = mesaj.get('text', {}).get('body', '').strip() if msg_type == 'text' else ''
        # Komut eşleştirme için sondaki noktalama işaretlerini temizle ("evet!" → "evet")
        metin    = re.sub(r'[.!?,;:]+$', '', metin).strip()
        ml       = metin.lower()

        # TTL kontrolü — son mesajdan bu yana 24 saat geçtiyse sıfırla
        if adim != 'hosgeldin':
            try:
                son = datetime.fromisoformat(session.get('son_mesaj', ''))
                if datetime.utcnow() - son > timedelta(minutes=SESSION_TTL_DAKIKA):
                    session.update(yeni_session())
                    self._hosgeldin_gonder(
                        phone_number_id, access_token, telefon, session, user,
                        prefix=f'⏰ {SESSION_TTL_DAKIKA} dakika işlem yapılmadığı için oturum sıfırlandı.\n\n')
                    session['son_mesaj'] = datetime.utcnow().isoformat()
                    return False
            except Exception:
                pass

        # Her mesajda son_mesaj güncelle
        session['son_mesaj'] = datetime.utcnow().isoformat()

        # Desteklenmeyen mesaj türleri
        if msg_type and msg_type not in ('text', 'image', 'location', 'contacts'):
            if msg_type in ('sticker', 'video', 'audio', 'voice', 'document', 'reaction'):
                wa.mesaj_gonder(phone_number_id, access_token, telefon,
                                '⚠️ Desteklenmez. Metin, konum, kişi kartı veya fotoğraf gönderin.')
            return False

        # Global komutlar
        _RESET = ('iptal', 'sıfırla', 'sifirla', 'reset', 'yeni', 'yenile', 'başlat', 'baslat',
                  'kapat', 'dur', 'q', 'çık', 'cik', '0')
        if _eslesir(ml, _RESET):
            session.update(yeni_session())
            self._hosgeldin_gonder(phone_number_id, access_token, telefon, session, user,
                                   prefix='🔄 Sıfırlandı.\n\n')
            return False

        if _eslesir(ml, ('durum', 'bakiye', 'kredi')):
            wa.mesaj_gonder(phone_number_id, access_token, telefon,
                            f'💳 Bakiye: {user.kredi:.0f} kredi')
            return False

        if _eslesir(ml, ('yardım', 'yardim', 'help', '?', 'nasıl', 'nasil')):
            self._hosgeldin_gonder(phone_number_id, access_token, telefon, session, user)
            return False

        if adim == 'hosgeldin':
            return self._isle_hosgeldin(
                telefon, mesaj, msg_type, metin, session,
                phone_number_id, access_token, user)
        elif adim == 'veri_toplama':
            return self._isle_veri_toplama(
                telefon, mesaj, msg_type, metin, session,
                phone_number_id, access_token, user)
        elif adim == 'onay_bekleniyor':
            return self._isle_onay(
                telefon, mesaj, msg_type, metin, session, phone_number_id, access_token, user)
        else:
            session['adim'] = 'hosgeldin'
            self._hosgeldin_gonder(phone_number_id, access_token, telefon, session, user)
            return False

    # ── ADIM: hosgeldin ───────────────────────────────────────────────────────────

    def _isle_hosgeldin(self, telefon, mesaj, msg_type, metin, session, pid, tok, user):
        ml_h = re.sub(r'[.!?,;:]+$', '', metin).lower().strip()

        # Link isteği hosgeldin'de de çalışsın
        if ml_h in ('link', 'form', 'web', 'url', 'bağlantı', 'baglanty'):
            session['adim'] = 'veri_toplama'
            self._link_gonder(telefon, session, pid, tok, user)
            return False

        # Şablon seçimi hosgeldin'de de çalışsın
        _sablon_h = {'1': 1, 'klasik': 1, '2': 2, 'modern': 2, '3': 3, 'minimalist': 3}
        if ml_h in _sablon_h:
            session['sablon_no'] = _sablon_h[ml_h]
            _isimler_h = {1: 'Klasik', 2: 'Modern', 3: 'Minimalist'}
            wa.mesaj_gonder(pid, tok, telefon,
                            f'🖨 Şablon: *{_isimler_h[_sablon_h[ml_h]]}* seçildi.')
            session['adim'] = 'veri_toplama'
            return False

        self._hosgeldin_gonder(pid, tok, telefon, session, user)
        session['adim'] = 'veri_toplama'

        _SELAMLAR = {'merhaba', 'selam', 'sa', 'hey', 'hi', 'hello', 'günaydın', 'iyi gunler', 'iyi akşamlar'}
        if msg_type in ('image', 'location', 'contacts') or (
                msg_type == 'text' and len(metin) >= 3 and ml_h not in _SELAMLAR):
            self._veri_isle(telefon, mesaj, msg_type, metin, session, pid, tok)
            if self.session_tamam_mi(session):
                session['adim'] = 'onay_bekleniyor'
                wa.mesaj_gonder(pid, tok, telefon, self._onay_metni(session))
        return False

    # ── ADIM: veri_toplama ────────────────────────────────────────────────────────

    def _isle_veri_toplama(self, telefon, mesaj, msg_type, metin, session, pid, tok, user):
        ml = re.sub(r'[.!?,;:]+$', '', metin).lower().strip()

        # Link isteği
        if _eslesir(ml, ('link', 'form', 'web', 'url', 'bağlantı', 'bagla')):
            self._link_gonder(telefon, session, pid, tok, user)
            return False

        # Şablon değiştirme
        _SABLON_STR = {'klasik': 1, 'modern': 2, 'minimalist': 3}
        if _eslesir(ml, ('şablon', 'sablon', 'template')):
            wa.mesaj_gonder(pid, tok, telefon,
                            '🖨 Şablon seçin:\n*1* klasik · *2* modern · *3* minimalist')
            return False
        _sablon_no = {'1': 1, '2': 2, '3': 3}.get(ml)
        if _sablon_no is None:
            _fuz = difflib.get_close_matches(ml, list(_SABLON_STR.keys()), n=1, cutoff=0.72)
            if _fuz:
                _sablon_no = _SABLON_STR[_fuz[0]]
        if _sablon_no is not None:
            session['sablon_no'] = _sablon_no
            isimler = {1: 'Klasik', 2: 'Modern', 3: 'Minimalist'}
            wa.mesaj_gonder(pid, tok, telefon,
                            f'🖨 Şablon: *{isimler[_sablon_no]}* seçildi.')
            return False

        # Özet (kısmi)
        if _eslesir(ml, ('özet', 'ozet', 'ne var', 'neredeyim')):
            wa.mesaj_gonder(pid, tok, telefon, self._kismi_ozet_metni(session))
            return False

        # Ada / parsel / m2 — "ada 15", "parsel 3", "m2 120" / "alan 120"
        _ada_m = re.match(r'^ada\s+(\S+)$', ml)
        if _ada_m:
            session['tasinmaz']['ada'] = _ada_m.group(1)
            wa.mesaj_gonder(pid, tok, telefon, f'✅ Ada: {_ada_m.group(1)}')
            return False
        _parsel_m = re.match(r'^parsel\s+(\S+)$', ml)
        if _parsel_m:
            session['tasinmaz']['parsel'] = _parsel_m.group(1)
            wa.mesaj_gonder(pid, tok, telefon, f'✅ Parsel: {_parsel_m.group(1)}')
            return False
        _alan_m = re.match(r'^(?:m2|alan|metrekare)\s+(\d+(?:[.,]\d+)?)$', ml)
        if _alan_m:
            try:
                session['tasinmaz']['alan_m2'] = float(_alan_m.group(1).replace(',', '.'))
                wa.mesaj_gonder(pid, tok, telefon, f'✅ Alan: {_alan_m.group(1)} m²')
            except Exception:
                pass
            return False

        # Fotoğraf silme
        if ml in ('foto sil', 'fotoğraf sil', 'fotografları sil', 'foto temizle') or \
                _eslesir(ml, ('fotosuz', 'foto yok')):
            session['fotograflar'] = []
            wa.mesaj_gonder(pid, tok, telefon, '🗑 Fotoğraflar silindi.')
            return False

        # Veriyi işle
        self._veri_isle(telefon, mesaj, msg_type, metin, session, pid, tok)

        # Tüm zorunlu alanlar doluysa onaya geç
        if self.session_tamam_mi(session):
            session['adim'] = 'onay_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, self._onay_metni(session))

        return False

    # ── ADIM: onay_bekleniyor ─────────────────────────────────────────────────────

    def _isle_onay(self, telefon, mesaj, msg_type, metin, session, pid, tok, user):
        ml = re.sub(r'[.!?,;:]+$', '', metin).lower().strip()

        # Link isteği onay'da da çalışır
        if _eslesir(ml, ('link', 'form', 'web', 'url', 'bağlantı')):
            self._link_gonder(telefon, session, pid, tok, user)
            return False

        # Fotoğraf onay ekranında da kabul edilir
        if msg_type == 'image':
            media_id = mesaj.get('image', {}).get('id')
            if media_id and len(session['fotograflar']) < self.MAX_FOTOGRAF:
                foto_bytes = wa.medya_indir(media_id, tok)
                if foto_bytes:
                    session['fotograflar'].append(foto_bytes)
            sayi = len(session['fotograflar'])
            kalan = self.MAX_FOTOGRAF - sayi
            bilgi = (f'📸 {sayi}/{self.MAX_FOTOGRAF} fotoğraf' +
                     (f' · {kalan} daha ekleyebilirsiniz.' if kalan > 0 else ' · Maksimum.'))
            wa.mesaj_gonder(pid, tok, telefon, bilgi + '\n\n' + self._onay_metni(session))
            return False

        # Yeni kişi kartı → alıcıyı güncelle, özette kal
        if msg_type == 'contacts':
            kisi = mesaj.get('contacts', [{}])[0]
            isim = kisi.get('name', {}).get('formatted_name', '')
            tels = kisi.get('phones', [{}])
            tel  = tels[0].get('phone', '') if tels else ''
            if isim:
                session['alici']['ad_soyad'] = isim
                if tel:
                    session['alici']['telefon'] = tel
            wa.mesaj_gonder(pid, tok, telefon,
                            f'👤 {isim} güncellendi.\n\n' + self._onay_metni(session))
            return False

        # Yeni konum → adresi güncelle, özette kal
        if msg_type == 'location':
            from app.services.whatsapp_client import konum_mesaji_isle
            loc = mesaj.get('location', {})
            session['konum'] = konum_mesaji_isle(loc)
            session['tasinmaz']['adres'] = (loc.get('address', '')
                                            or session['konum'].get('adres', ''))
            wa.mesaj_gonder(pid, tok, telefon,
                            f'📍 Konum güncellendi.\n\n' + self._onay_metni(session))
            return False

        # Onay
        _EVET = ('evet', 'onayla', 'onay', 'ok', 'tamam', 'e', 'y', 'yes', '✓', '✅',
                 'gönder', 'gonder', 'oluştur', 'olustur', 'hazır', 'hazir',
                 'bitti', 'yazdır', 'yazdir', 'onayladım', 'onayladim',
                 'onaylıyorum', 'onayliyorum', 'yap', 'üret', 'uret')
        if _eslesir(ml, _EVET):
            return self._belge_uret(telefon, session, pid, tok, user)

        # Hayır → ne düzelteceğini sor
        if _eslesir(ml, ('hayır', 'hayir', 'h', 'n', 'no', 'değil', 'degil')):
            wa.mesaj_gonder(pid, tok, telefon,
                            '✏️ Ne düzeltelim?\n\n'
                            '*ad* · *adres* · *fiyat* · *tür*\n'
                            '*tc* · *tel* · *komisyon* · *şablon*')
            return False

        # Alan düzeltme komutları
        if _eslesir(ml, ('alici', 'alıcı', 'isim', 'ad', 'müşteri', 'musteri', 'name')):
            session['alici']['ad_soyad'] = None
            session['adim'] = 'veri_toplama'
            wa.mesaj_gonder(pid, tok, telefon,
                            '👤 Alıcı adını girin _(kişi kartı veya metin)_')
            return False

        if _eslesir(ml, ('adres', 'tasinmaz', 'taşınmaz', 'konum', 'yer', 'lokasyon')):
            session['tasinmaz']['adres'] = None
            session['konum'] = None
            session['adim'] = 'veri_toplama'
            wa.mesaj_gonder(pid, tok, telefon,
                            '📍 Adresi veya konumu gönderin:')
            return False

        if _eslesir(ml, ('fiyat', 'bedel', 'ücret', 'ucret', 'para', 'tutar')):
            session['fiyat'] = None
            session['adim'] = 'veri_toplama'
            wa.mesaj_gonder(pid, tok, telefon,
                            '💰 Fiyatı TL olarak girin:')
            return False

        if _eslesir(ml, ('tur', 'tür', 'islem', 'işlem', 'tip')):
            session['islem_turu'] = None
            session['adim'] = 'veri_toplama'
            wa.mesaj_gonder(pid, tok, telefon,
                            '🔑 İşlem türü: *kiralık* veya *satılık*')
            return False

        # İşlem türünü direkt değiştir
        if _eslesir(ml, ('kiralık', 'kiralik', 'kira', 'kiralama')):
            session['islem_turu'] = 'kira'
            session['komisyon_satis_yuzde'] = None
            wa.mesaj_gonder(pid, tok, telefon, '🔑 Kiralama seçildi.\n\n' + self._onay_metni(session))
            return False

        if _eslesir(ml, ('satılık', 'satilik', 'satış', 'satis', 'sat')):
            session['islem_turu'] = 'satis'
            session['komisyon_kira_ay'] = None
            wa.mesaj_gonder(pid, tok, telefon, '🔑 Satış seçildi.\n\n' + self._onay_metni(session))
            return False

        if ml in ('tc', 'kimlik', 'tc no', 'tcno', 'tckn') or \
                _eslesir(ml, ('kimlik', 'tcno', 'tckn')):
            session['alici']['tc_no'] = None
            session['adim'] = 'veri_toplama'
            wa.mesaj_gonder(pid, tok, telefon,
                            '🪪 TC kimlik numarasını girin (11 hane):')
            return False

        if _eslesir(ml, ('telefon', 'tel', 'gsm', 'cep', 'numara')):
            session['alici']['telefon'] = None
            session['adim'] = 'veri_toplama'
            wa.mesaj_gonder(pid, tok, telefon,
                            '📞 Telefon numarasını girin:')
            return False

        if _eslesir(ml, ('komisyon', 'kom')):
            session['komisyon_kira_ay'] = None
            session['komisyon_satis_yuzde'] = None
            session['adim'] = 'veri_toplama'
            if session.get('islem_turu') == 'kira':
                wa.mesaj_gonder(pid, tok, telefon, '📊 Kira komisyonu (ay sayısı):')
            else:
                wa.mesaj_gonder(pid, tok, telefon, '📊 Satış komisyonu (%):')
            return False

        # Fotoğraf silme onay ekranında da çalışır
        if ml in ('foto sil', 'fotoğraf sil', 'fotografları sil', 'foto temizle') or \
                _eslesir(ml, ('fotosuz', 'foto yok')):
            session['fotograflar'] = []
            wa.mesaj_gonder(pid, tok, telefon, '🗑 Fotoğraflar silindi.\n\n' + self._onay_metni(session))
            return False

        # Şablon değiştirme
        if _eslesir(ml, ('şablon', 'sablon', 'template')):
            wa.mesaj_gonder(pid, tok, telefon,
                            '🖨 Şablon seçin:\n*1* klasik · *2* modern · *3* minimalist')
            return False
        _SABLON_STR2 = {'klasik': 1, 'modern': 2, 'minimalist': 3}
        _sablon_no2 = {'1': 1, '2': 2, '3': 3}.get(ml)
        if _sablon_no2 is None:
            _fuz2 = difflib.get_close_matches(ml, list(_SABLON_STR2.keys()), n=1, cutoff=0.72)
            if _fuz2:
                _sablon_no2 = _SABLON_STR2[_fuz2[0]]
        if _sablon_no2 is not None:
            session['sablon_no'] = _sablon_no2
            _isimler = {1: 'Klasik', 2: 'Modern', 3: 'Minimalist'}
            wa.mesaj_gonder(pid, tok, telefon,
                            f'🖨 Şablon: *{_isimler[_sablon_no2]}*\n\n' + self._onay_metni(session))
            return False

        # Sayı yazılırsa fiyat güncellemesi
        if msg_type == 'text' and metin:
            sayi_m = re.fullmatch(r'[\d.,]+', metin.strip())
            if sayi_m:
                try:
                    yeni_fiyat = str(int(float(
                        metin.strip().replace('.', '').replace(',', '.')
                    )))
                    session['fiyat'] = yeni_fiyat
                    wa.mesaj_gonder(pid, tok, telefon,
                                    f'💰 Fiyat güncellendi: {yeni_fiyat} TL\n\n' + self._onay_metni(session))
                    return False
                except Exception:
                    pass

        # Bilinmeyen metin → özeti tekrar göster
        wa.mesaj_gonder(pid, tok, telefon, self._onay_metni(session))
        return False

    # ── VERİ İŞLEME ──────────────────────────────────────────────────────────────

    def _veri_isle(self, telefon, mesaj, msg_type, metin, session, pid, tok):
        """Gelen mesajı tipine göre parse edip session'a ekle."""
        guncellendi = []

        if msg_type == 'image':
            media_id = mesaj.get('image', {}).get('id')
            if media_id and len(session['fotograflar']) < self.MAX_FOTOGRAF:
                foto_bytes = wa.medya_indir(media_id, tok)
                if foto_bytes:
                    session['fotograflar'].append(foto_bytes)
            sayi  = len(session['fotograflar'])
            kalan = self.MAX_FOTOGRAF - sayi
            bilgi = (f'📸 {sayi}/{self.MAX_FOTOGRAF} fotoğraf alındı.'
                     + (f' {kalan} daha ekleyebilirsiniz.' if kalan > 0 else ' Maksimum.'))
            wa.mesaj_gonder(pid, tok, telefon, bilgi)
            return  # Fotoğraf için ayrı eksik alanı tekrar sorma

        elif msg_type == 'location':
            from app.services.whatsapp_client import konum_mesaji_isle
            loc = mesaj.get('location', {})
            session['konum'] = konum_mesaji_isle(loc)
            session['tasinmaz']['adres'] = (loc.get('address', '')
                                            or session['konum'].get('adres', ''))
            guncellendi.append(f'📍 Konum: {session["konum"].get("adres", "alındı")}')

        elif msg_type == 'contacts':
            kisi = mesaj.get('contacts', [{}])[0]
            isim = kisi.get('name', {}).get('formatted_name', '')
            tels = kisi.get('phones', [{}])
            tel  = tels[0].get('phone', '') if tels else ''
            if isim:
                session['alici']['ad_soyad'] = isim
                if tel:
                    session['alici']['telefon'] = tel
                guncellendi.append(f'👤 {isim}' + (f' · {tel}' if tel else ''))

        elif msg_type == 'text' and metin:
            from app.services.metin_parse import yer_gosterme_parse_et
            bilgi = yer_gosterme_parse_et(metin)

            if bilgi.get('alici_ad') and not session['alici']['ad_soyad']:
                session['alici']['ad_soyad'] = bilgi['alici_ad']
                guncellendi.append(f'👤 {bilgi["alici_ad"]}')
            if bilgi.get('alici_tc') and not session['alici']['tc_no']:
                session['alici']['tc_no'] = bilgi['alici_tc']
            if bilgi.get('alici_tel') and not session['alici']['telefon']:
                session['alici']['telefon'] = bilgi['alici_tel']

            if bilgi.get('adres') and not session['tasinmaz']['adres']:
                session['tasinmaz']['adres'] = bilgi['adres']
                guncellendi.append(f'📍 {bilgi["adres"][:60]}')
            for alan in ('sehir', 'ilce', 'mahalle'):
                if bilgi.get(alan):
                    session['tasinmaz'][alan] = bilgi[alan]

            if bilgi.get('islem_turu') and not session['islem_turu']:
                session['islem_turu'] = bilgi['islem_turu']
                guncellendi.append('🔑 ' + ('Kiralama' if bilgi['islem_turu'] == 'kira' else 'Satış'))

            if bilgi.get('fiyat') and not session['fiyat']:
                try:
                    session['fiyat'] = str(int(float(str(bilgi['fiyat']).replace('.', '').replace(',', '.'))))
                except Exception:
                    session['fiyat'] = str(bilgi['fiyat'])
                guncellendi.append(f'💰 {session["fiyat"]} TL')

            if bilgi.get('komisyon_ay') is not None and session['komisyon_kira_ay'] is None:
                session['komisyon_kira_ay'] = bilgi['komisyon_ay']
            if bilgi.get('komisyon_yuzde') is not None and session['komisyon_satis_yuzde'] is None:
                session['komisyon_satis_yuzde'] = bilgi['komisyon_yuzde']

        # Güncelleme özeti + bir sonraki adım
        if guncellendi:
            eksik = self._eksik_alanlar(session)
            satir = '✅ ' + ' · '.join(guncellendi)
            if eksik:
                satir += '\n📝 Eksik: ' + ' · '.join(eksik)
            wa.mesaj_gonder(pid, tok, telefon, satir)
        else:
            # Anlamadık ama bunu söyleme — sıradaki adımı sor
            rehber = self._sonraki_adim(session)
            if rehber:
                wa.mesaj_gonder(pid, tok, telefon, rehber)

    def _eksik_alanlar(self, session) -> list:
        eksik = []
        if not session.get('alici', {}).get('ad_soyad'):
            eksik.append('ad')
        if not (session.get('tasinmaz', {}).get('adres') or session.get('konum')):
            eksik.append('adres')
        if not session.get('islem_turu'):
            eksik.append('kira/satış')
        if not session.get('fiyat'):
            eksik.append('fiyat')
        return eksik

    def _sonraki_adim(self, session: dict) -> str:
        """Sıradaki eksik alan için tek cümlelik yönlendirme."""
        if not session.get('alici', {}).get('ad_soyad'):
            return '👤 Alıcının adını yazın veya kişi kartı gönderin.'
        if not (session.get('tasinmaz', {}).get('adres') or session.get('konum')):
            return '📍 Taşınmazın konumunu paylaşın veya adresini yazın.'
        if not session.get('islem_turu'):
            return '💬 _kiralık 15000_ veya _satılık 450000_ yazın.'
        if not session.get('fiyat'):
            return '💰 Fiyatı yazın. Örnek: _18000_'
        return ''

    # ── LINK GÖNDER ───────────────────────────────────────────────────────────────

    def _link_gonder(self, telefon, session, pid, tok, user):
        from app.models import db, HizliFormToken
        from flask import current_app
        import uuid

        token_str = uuid.uuid4().hex
        hft = HizliFormToken(
            token=token_str,
            user_id=user.id,
            telefon=telefon,
            phone_number_id=pid,
            access_token=tok,
        )
        db.session.add(hft)
        db.session.commit()

        frontend_url = current_app.config.get('FRONTEND_URL', '').rstrip('/')
        link = f'{frontend_url}/hizli-form/{token_str}'
        wa.mesaj_gonder(pid, tok, telefon,
                        f'🔗 *Hızlı Form*\n\n'
                        f'Formu doldurun, PDF otomatik WhatsApp\'a gelir:\n'
                        f'{link}\n\n'
                        f'_24 saat geçerlidir._')

    # ── BELGE ÜRET ────────────────────────────────────────────────────────────────

    def _belge_uret(self, telefon, session, pid, tok, user) -> bool:
        from app.models import db, EmlakciProfil, YerGosterme, IslemLog
        from app.services.sektorler.emlak_pdf import pdf_olustur
        from app.services.belge_store import kaydet
        from app.services import kayit_akisi as kayit
        from flask import current_app

        # Önce profil kontrolü — kredi düşmeden önce yapılmalı
        profil = EmlakciProfil.query.filter_by(user_id=user.id).first()
        if not profil:
            frontend_url = current_app.config.get('FRONTEND_URL', '')
            wa.mesaj_gonder(pid, tok, telefon,
                            f'⚠️ Önce emlakçı profilinizi tamamlayın:\n'
                            f'🔗 {frontend_url}/emlak-profil')
            return False

        if not kayit.kredi_dus(user, self.KREDI_MALIYETI):
            frontend_url = current_app.config.get('FRONTEND_URL', '').rstrip('/')
            wa.mesaj_gonder(pid, tok, telefon,
                            f'❌ Yetersiz kredi ({user.kredi:.0f}/{self.KREDI_MALIYETI})\n\n'
                            f'💳 Kredi satın almak için:\n{frontend_url}/kredi')
            return False

        # Komisyon belirtilmemişse profil varsayılanını kullan (0 geçerli değer, None değil)
        if session.get('islem_turu') == 'kira' and session.get('komisyon_kira_ay') is None:
            session['komisyon_kira_ay'] = profil.komisyon_kira_ay if profil.komisyon_kira_ay is not None else 1
        if session.get('islem_turu') == 'satis' and session.get('komisyon_satis_yuzde') is None:
            session['komisyon_satis_yuzde'] = profil.komisyon_satis_yuzde if profil.komisyon_satis_yuzde is not None else 2.0

        try:
            pdf_bytes = pdf_olustur(session, profil)
        except Exception as e:
            logger.error(f'[Emlak] PDF hatası: {e}', exc_info=True)
            wa.mesaj_gonder(pid, tok, telefon,
                            '❌ PDF oluşturulurken hata oluştu. Tekrar deneyin.')
            return False

        token_str = kaydet(pdf_bytes, 'pdf')
        base_url  = current_app.config.get('BASE_URL', '').rstrip('/')
        pdf_url   = f'{base_url}/api/belge/{token_str}'

        try:
            alici    = session.get('alici', {})
            tasinmaz = session.get('tasinmaz', {})
            konum    = session.get('konum') or {}
            yg = YerGosterme(
                user_id=user.id,
                alici_ad_soyad=alici.get('ad_soyad'),
                alici_adres=alici.get('adres'),
                alici_tc_no=alici.get('tc_no'),
                alici_telefon=alici.get('telefon'),
                tasinmaz_sehir=tasinmaz.get('sehir'),
                tasinmaz_ilce=tasinmaz.get('ilce'),
                tasinmaz_mahalle=tasinmaz.get('mahalle'),
                tasinmaz_ada=tasinmaz.get('ada'),
                tasinmaz_parsel=tasinmaz.get('parsel'),
                tasinmaz_adres=tasinmaz.get('adres') or konum.get('adres'),
                tasinmaz_alan=str(tasinmaz.get('alan_m2') or ''),
                konum_lat=konum.get('lat'),
                konum_lng=konum.get('lng'),
                islem_turu=session.get('islem_turu'),
                fiyat=session.get('fiyat'),
                komisyon_kira_ay=session.get('komisyon_kira_ay'),
                komisyon_satis_yuzde=session.get('komisyon_satis_yuzde'),
                sablon_no=session.get('sablon_no', 1),
                fotografli_mi=len(session.get('fotograflar', [])) > 0,
                pdf_token=token_str,
                pdf_url=pdf_url,
                sozlesme_tarihi=date.today(),
            )
            db.session.add(yg)
            db.session.flush()
            log = IslemLog(
                user_id=user.id,
                telefon=telefon,
                sektor='emlak',
                islem_tipi='yer_gosterme',
                durum='tamamlandi',
                kredi_kullanim=self.KREDI_MALIYETI,
                detay={'yer_gosterme_id': yg.id},
            )
            db.session.add(log)
            yg.islem_log_id = log.id
            db.session.commit()
        except Exception as e:
            logger.error(f'[Emlak] Kayıt hatası: {e}', exc_info=True)

        alici_adi   = session.get('alici', {}).get('ad_soyad', 'Alıcı')
        belge_fmt   = getattr(profil, 'belge_format', 'pdf') or 'pdf'
        dosya_adi   = f'yer_gosterme_{date.today().strftime("%Y%m%d")}.pdf'
        baslik_mesaj = f'✅ {alici_adi} için Yer Gösterme Sözleşmesi hazır!'

        if belge_fmt in ('pdf', 'ikisi'):
            wa.belge_gonder(pid, tok, telefon, pdf_url, dosya_adi, baslik_mesaj)

        if belge_fmt in ('resim', 'ikisi'):
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(stream=pdf_bytes, filetype='pdf')
                pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                png_bytes = pix.tobytes('png')
                png_token = kaydet(png_bytes, 'png')
                png_url   = f'{base_url}/api/belge/{png_token}'
                caption   = baslik_mesaj if belge_fmt == 'resim' else ''
                wa.resim_gonder(pid, tok, telefon, png_url, caption)
            except Exception as e:
                logger.error(f'[Emlak] PDF→resim dönüşüm hatası: {e}')
                if belge_fmt == 'resim':
                    wa.belge_gonder(pid, tok, telefon, pdf_url, dosya_adi, baslik_mesaj)

        logger.info(f'[Emlak] Belge gönderildi ({belge_fmt}) → {telefon}')

        # Kredi bitmek üzereyse uyar
        if user.kredi < self.KREDI_MALIYETI:
            frontend_url = current_app.config.get('FRONTEND_URL', '').rstrip('/')
            wa.mesaj_gonder(pid, tok, telefon,
                            f'⚠️ Krediniz bitti ({user.kredi:.0f} kaldı).\n{frontend_url}/kredi')

        return True

    # ── MESAJ METİNLERİ ─────────────────────────────────────────────────────────

    def _kismi_ozet_metni(self, session: dict) -> str:
        """Veri_toplama aşamasında kısmi durum özeti."""
        alici    = session.get('alici', {})
        tasinmaz = session.get('tasinmaz', {})
        konum    = session.get('konum') or {}
        satirlar = ['📊 *Mevcut durum*\n']

        ad = alici.get('ad_soyad')
        satirlar.append(f'👤 Ad: {ad or "—"}')
        adres = tasinmaz.get('adres') or konum.get('adres')
        satirlar.append(f'📍 Adres: {adres[:50] + "..." if adres and len(adres) > 50 else adres or "—"}')
        islem = session.get('islem_turu')
        satirlar.append(f'🔑 Tür: {"Kiralama" if islem == "kira" else "Satış" if islem == "satis" else "—"}')
        satirlar.append(f'💰 Fiyat: {session.get("fiyat") + " TL" if session.get("fiyat") else "—"}')
        foto = len(session.get('fotograflar', []))
        if foto:
            satirlar.append(f'📸 Fotoğraf: {foto}/{self.MAX_FOTOGRAF}')

        eksik = self._eksik_alanlar(session)
        if eksik:
            satirlar.append(f'\n📝 Eksik: ' + ' · '.join(eksik))
        else:
            satirlar.append('\n✅ Tüm zorunlu alanlar dolu!')
        return '\n'.join(satirlar)

    def _hosgeldin_metni(self, form_url: str = '') -> str:
        try:
            from flask import current_app
            frontend_url = current_app.config.get('FRONTEND_URL', '').rstrip('/')
            komut_url = f'{frontend_url}/komutlar'
        except Exception:
            komut_url = ''

        form_satiri  = f'\n*2 —* 🌐 {form_url}' if form_url else ''
        komut_satiri = f'\n\n📖 {komut_url}' if komut_url else ''

        return (
            '🏠 *Yer Gösterme Sözleşmesi*\n\n'
            '*1 —* 👤 Kişi kartı · 📍 Konum · 📸 Resim · 💬 _kiralık 15000_ yada _satılık 450000_'
            + form_satiri +
            '\n*3 —* ✍️ _Ali Veli 0532... Kadıköy kiralık 18000_'
            + komut_satiri
        )

    def _hosgeldin_gonder(self, pid, tok, telefon, session, user, prefix: str = ''):
        """Form token'ı üret, URL'yi hoşgeldin metnine göm ve gönder."""
        form_url = ''
        try:
            from app.models import db, HizliFormToken
            from flask import current_app
            import uuid
            token_str = uuid.uuid4().hex
            db.session.add(HizliFormToken(
                token=token_str,
                user_id=user.id,
                telefon=telefon,
                phone_number_id=pid,
                access_token=tok,
            ))
            db.session.commit()
            frontend_url = current_app.config.get('FRONTEND_URL', '').rstrip('/')
            form_url = f'{frontend_url}/hizli-form/{token_str}'
        except Exception:
            pass

        metin = self._hosgeldin_metni(form_url)
        if prefix:
            metin = prefix + metin
        wa.mesaj_gonder(pid, tok, telefon, metin)

    def _onay_metni(self, session: dict) -> str:
        alici    = session.get('alici', {})
        tasinmaz = session.get('tasinmaz', {})
        konum    = session.get('konum') or {}
        islem_tr = 'Kiralama' if session.get('islem_turu') == 'kira' else 'Satış'
        adres    = tasinmaz.get('adres') or konum.get('adres') or '—'
        alici_ad = alici.get('ad_soyad') or '—'
        tc       = alici.get('tc_no') or '—'
        tel      = alici.get('telefon') or '—'
        foto     = len(session.get('fotograflar', []))
        sablon_adlari = {1: 'Klasik', 2: 'Modern', 3: 'Minimalist'}
        komisyon = '—'
        if session.get('islem_turu') == 'kira':
            k = session.get('komisyon_kira_ay')
            komisyon = f'{k} aylık kira' if k is not None else '(profil varsayılanı)'
        elif session.get('islem_turu') == 'satis':
            k = session.get('komisyon_satis_yuzde')
            komisyon = f'%{k}' if k is not None else '(profil varsayılanı)'

        return (
            '📋 *Özet — Onaylıyor musunuz?*\n\n'
            f'🖨 {sablon_adlari.get(session.get("sablon_no", 1))}'
            f'{"  📸 " + str(foto) + " fotoğraf" if foto > 0 else ""}\n'
            f'🔑 {islem_tr}  💰 {session.get("fiyat", "—")} TL'
            f'{"  📊 " + komisyon if komisyon != "—" else ""}\n'
            f'👤 {alici_ad}'
            f'{"  🪪 " + tc if tc != "—" else ""}'
            f'{"  📞 " + tel if tel != "—" else ""}\n'
            f'📍 {adres[:70]}{"..." if len(adres) > 70 else ""}\n\n'
            '✅ *evet* → Belgeyi oluştur\n'
            '✏️ Düzelt: *ad* · *adres* · *fiyat* · *tür* · *tc* · *tel* · *komisyon* · *şablon*\n'
            '❌ *kapat* → Baştan başla'
        )
