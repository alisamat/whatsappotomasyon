"""
EMLAK SEKTÖRÜ — Yer Gösterme Sözleşmesi
State machine ile adım adım veri toplama
"""
import logging
from datetime import date
from app.services.sektorler.base import BaseSektorHandler
from app.services import whatsapp_client as wa

logger = logging.getLogger(__name__)

ADIMLAR = [
    'menu', 'foto_secim', 'islem_turu', 'alici_bekleniyor',
    'tasinmaz_bekleniyor', 'fiyat_bekleniyor', 'komisyon_bekleniyor',
    'foto_bekleniyor', 'onay_bekleniyor',
]


def yeni_session() -> dict:
    return {
        'adim': 'menu',
        'sablon_no': 1,
        'fotografli_mi': True,
        'islem_turu': None,
        'fotograflar': [],
        'konum': None,
        'alici': {'ad_soyad': None, 'tc_no': None, 'telefon': None, 'adres': None},
        'tasinmaz': {'sehir': None, 'ilce': None, 'mahalle': None, 'ada': None,
                     'parsel': None, 'adres': None, 'alan_m2': None},
        'fiyat': None,
        'komisyon_kira_ay': None,
        'komisyon_satis_yuzde': None,
    }


class EmlakHandler(BaseSektorHandler):
    SEKTOR_KODU    = 'emlak'
    KREDI_MALIYETI = 5
    MIN_FOTOGRAF   = 1
    MAX_FOTOGRAF   = 4

    def session_tamam_mi(self, session: dict) -> bool:
        """Tüm zorunlu veriler tamamlandı mı?"""
        return (
            session.get('alici', {}).get('ad_soyad') and
            (session.get('tasinmaz', {}).get('adres') or session.get('konum')) and
            session.get('islem_turu') and
            session.get('fiyat')
        )

    def beklenen_veri_mesaji(self) -> str:
        return (
            '🏠 *Yer Gösterme Belgesi*\n\n'
            'Başlamak için *1* yazın.'
        )

    def mesaj_isle(self, telefon: str, mesaj: dict, session: dict,
                   phone_number_id: str, access_token: str, user) -> bool:
        """
        Gelen mesajı session adımına göre işle.
        True döndürürse işlem tamamlandı demektir.
        """
        adim = session.get('adim', 'menu')
        msg_type = mesaj.get('type', '')
        metin    = mesaj.get('text', {}).get('body', '').strip() if msg_type == 'text' else ''
        metin_lower = metin.lower()

        # Global komutlar
        if metin_lower in ('iptal', 'sıfırla', 'reset', 'yeni', '0'):
            session.update(yeni_session())
            wa.mesaj_gonder(phone_number_id, access_token, telefon,
                            '🔄 Sıfırlandı.\n\n' + self._menu_metni())
            return False

        if metin_lower in ('durum', 'bakiye', 'kredi'):
            wa.mesaj_gonder(phone_number_id, access_token, telefon,
                            f'💳 Kredi bakiyeniz: {user.kredi:.0f}')
            return False

        # Adım yönlendirici
        if adim == 'menu':
            return self._isle_menu(telefon, metin, session, phone_number_id, access_token)
        elif adim == 'foto_secim':
            return self._isle_foto_secim(telefon, metin, session, phone_number_id, access_token)
        elif adim == 'islem_turu':
            return self._isle_islem_turu(telefon, metin, session, phone_number_id, access_token)
        elif adim == 'alici_bekleniyor':
            return self._isle_alici(telefon, mesaj, msg_type, metin, session, phone_number_id, access_token)
        elif adim == 'tasinmaz_bekleniyor':
            return self._isle_tasinmaz(telefon, mesaj, msg_type, metin, session, phone_number_id, access_token)
        elif adim == 'fiyat_bekleniyor':
            return self._isle_fiyat(telefon, metin, session, phone_number_id, access_token)
        elif adim == 'komisyon_bekleniyor':
            return self._isle_komisyon(telefon, metin, session, phone_number_id, access_token, user)
        elif adim == 'foto_bekleniyor':
            return self._isle_foto(telefon, mesaj, msg_type, metin, session, phone_number_id, access_token)
        elif adim == 'onay_bekleniyor':
            return self._isle_onay(telefon, metin, session, phone_number_id, access_token, user)
        else:
            session['adim'] = 'menu'
            wa.mesaj_gonder(phone_number_id, access_token, telefon, self._menu_metni())
            return False

    def handle(self, telefon: str, session: dict, phone_number_id: str, access_token: str) -> bool:
        """Eski akış uyumluluğu — artık kullanılmıyor."""
        return False

    # ── ADIM İŞLEYİCİLER ─────────────────────────────────────────────────────

    def _isle_menu(self, telefon, metin, session, pid, tok):
        if metin in ('1', '2', '3'):
            session['sablon_no'] = int(metin)
            session['adim'] = 'foto_secim'
            wa.mesaj_gonder(pid, tok, telefon, self._foto_secim_metni())
        else:
            wa.mesaj_gonder(pid, tok, telefon, self._menu_metni())
        return False

    def _isle_foto_secim(self, telefon, metin, session, pid, tok):
        m = metin.lower()
        if m in ('e', 'evet', 'e️⃣'):
            session['fotografli_mi'] = True
            session['adim'] = 'islem_turu'
            wa.mesaj_gonder(pid, tok, telefon, self._islem_turu_metni())
        elif m in ('h', 'hayır', 'hayir'):
            session['fotografli_mi'] = False
            session['adim'] = 'islem_turu'
            wa.mesaj_gonder(pid, tok, telefon, self._islem_turu_metni())
        else:
            wa.mesaj_gonder(pid, tok, telefon, self._foto_secim_metni())
        return False

    def _isle_islem_turu(self, telefon, metin, session, pid, tok):
        m = metin.lower()
        if m in ('k', 'kira', 'kiralama'):
            session['islem_turu'] = 'kira'
            session['adim'] = 'alici_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, self._alici_metni())
        elif m in ('s', 'satis', 'satış', 'satish'):
            session['islem_turu'] = 'satis'
            session['adim'] = 'alici_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, self._alici_metni())
        else:
            wa.mesaj_gonder(pid, tok, telefon, self._islem_turu_metni())
        return False

    def _isle_alici(self, telefon, mesaj, msg_type, metin, session, pid, tok):
        from app.services.metin_parse import alici_detay_parse_et

        if msg_type == 'contacts':
            kisi = mesaj.get('contacts', [{}])[0]
            isim = kisi.get('name', {}).get('formatted_name', '')
            tels = kisi.get('phones', [{}])
            tel  = tels[0].get('phone', '') if tels else ''
            session['alici'] = {'ad_soyad': isim, 'tc_no': None, 'telefon': tel, 'adres': None}
            session['adim'] = 'tasinmaz_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon,
                            f'👤 Alıcı: *{isim}*{(" · " + tel) if tel else ""}\n\n'
                            + self._tasinmaz_metni())
        elif msg_type == 'text' and metin:
            bilgi = alici_detay_parse_et(metin)
            session['alici'] = {
                'ad_soyad': bilgi.get('ad_soyad') or metin,
                'tc_no':    bilgi.get('tc_no'),
                'telefon':  bilgi.get('telefon'),
                'adres':    bilgi.get('adres'),
            }
            session['adim'] = 'tasinmaz_bekleniyor'
            isim = session['alici']['ad_soyad']
            tc   = bilgi.get('tc_no') or ''
            tel  = bilgi.get('telefon') or ''
            ozet = f'👤 Alıcı: *{isim}*'
            if tc:  ozet += f'\n🪪 TC: {tc[:3]}****{tc[-4:] if len(tc) >= 7 else tc}'
            if tel: ozet += f'\n📞 Tel: {tel}'
            wa.mesaj_gonder(pid, tok, telefon, ozet + '\n\n' + self._tasinmaz_metni())
        else:
            wa.mesaj_gonder(pid, tok, telefon, self._alici_metni())
        return False

    def _isle_tasinmaz(self, telefon, mesaj, msg_type, metin, session, pid, tok):
        from app.services.metin_parse import tasinmaz_parse_et

        if msg_type == 'location':
            loc = mesaj.get('location', {})
            from app.services.whatsapp_client import konum_mesaji_isle
            session['konum'] = konum_mesaji_isle(loc)
            # Adres taşınmaz bilgisine de aktar
            session['tasinmaz']['adres'] = loc.get('address', '') or session['konum'].get('adres', '')
            session['adim'] = 'fiyat_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon,
                            f'📍 Konum alındı: {session["konum"].get("adres", "")}\n\n'
                            + self._fiyat_metni(session['islem_turu']))
        elif msg_type == 'text' and metin:
            bilgi = tasinmaz_parse_et(metin)
            session['tasinmaz'].update({k: v for k, v in bilgi.items() if v})
            if not session['tasinmaz'].get('adres'):
                session['tasinmaz']['adres'] = metin
            session['adim'] = 'fiyat_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon,
                            f'📍 Adres alındı: *{session["tasinmaz"]["adres"]}*\n\n'
                            + self._fiyat_metni(session['islem_turu']))
        else:
            wa.mesaj_gonder(pid, tok, telefon, self._tasinmaz_metni())
        return False

    def _isle_fiyat(self, telefon, metin, session, pid, tok):
        import re
        fiyat_match = re.search(r'[\d.,]+', metin.replace(' ', ''))
        if fiyat_match:
            session['fiyat'] = fiyat_match.group().replace(',', '.')
            session['adim'] = 'komisyon_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, self._komisyon_metni(session))
        else:
            wa.mesaj_gonder(pid, tok, telefon, self._fiyat_metni(session['islem_turu']))
        return False

    def _isle_komisyon(self, telefon, metin, session, pid, tok, user):
        import re
        m = metin.lower().strip()
        if m in ('atla', 'varsayilan', 'varsayılan', '-', 'ok'):
            # Varsayılan komisyon kullan
            pass
        elif session['islem_turu'] == 'kira':
            ay_match = re.search(r'\d+', m)
            if ay_match:
                session['komisyon_kira_ay'] = int(ay_match.group())
        else:
            yuz_match = re.search(r'[\d.]+', m)
            if yuz_match:
                session['komisyon_satis_yuzde'] = float(yuz_match.group())

        if session['fotografli_mi']:
            session['adim'] = 'foto_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, self._foto_metni())
        else:
            session['adim'] = 'onay_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, self._onay_metni(session))
        return False

    def _isle_foto(self, telefon, mesaj, msg_type, metin, session, pid, tok):
        if msg_type == 'image':
            media_id = mesaj.get('image', {}).get('id')
            if media_id and len(session['fotograflar']) < self.MAX_FOTOGRAF:
                foto_bytes = wa.medya_indir(media_id, tok)
                if foto_bytes:
                    session['fotograflar'].append(foto_bytes)
            sayi  = len(session['fotograflar'])
            kalan = self.MAX_FOTOGRAF - sayi
            if sayi >= self.MAX_FOTOGRAF:
                session['adim'] = 'onay_bekleniyor'
                wa.mesaj_gonder(pid, tok, telefon,
                                f'📸 {self.MAX_FOTOGRAF} fotoğraf alındı.\n\n'
                                + self._onay_metni(session))
            else:
                wa.mesaj_gonder(pid, tok, telefon,
                                f'📸 Fotoğraf {sayi}/{self.MAX_FOTOGRAF} alındı. '
                                f'{kalan} daha ekleyebilir veya *tamam* yazabilirsiniz.')
        elif msg_type == 'text' and metin.lower() in ('tamam', 'yeter', 'bitti', 'ok', 'devam'):
            if not session['fotograflar']:
                session['fotografli_mi'] = False
            session['adim'] = 'onay_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, self._onay_metni(session))
        else:
            wa.mesaj_gonder(pid, tok, telefon, self._foto_metni())
        return False

    def _isle_onay(self, telefon, metin, session, pid, tok, user):
        m = metin.lower().strip()
        if m in ('evet', 'onayla', 'onay', 'ok', 'tamam', 'e'):
            return self._belge_uret(telefon, session, pid, tok, user)
        elif m in ('alici', 'alıcı'):
            session['adim'] = 'alici_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, '🔄 Alıcı bilgisini tekrar girin:\n\n' + self._alici_metni())
        elif m in ('tasinmaz', 'taşınmaz', 'adres', 'konum'):
            session['adim'] = 'tasinmaz_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, '🔄 Taşınmaz bilgisini tekrar girin:\n\n' + self._tasinmaz_metni())
        elif m in ('fiyat', 'bedel'):
            session['adim'] = 'fiyat_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, '🔄 Fiyatı tekrar girin:\n\n' + self._fiyat_metni(session['islem_turu']))
        else:
            wa.mesaj_gonder(pid, tok, telefon, self._onay_metni(session))
        return False

    def _belge_uret(self, telefon, session, pid, tok, user) -> bool:
        from app.models import db, EmlakciProfil, YerGosterme, IslemLog
        from app.services.sektorler.emlak_pdf import pdf_olustur
        from app.services.belge_store import kaydet
        from app.services import kayit_akisi as kayit
        from flask import current_app

        # Kredi kontrolü
        if not kayit.kredi_dus(user, self.KREDI_MALIYETI):
            wa.mesaj_gonder(pid, tok, telefon,
                            f'❌ Yetersiz kredi. Belge için {self.KREDI_MALIYETI} kredi gerekli.\n'
                            f'💳 Mevcut bakiye: {user.kredi:.0f} kredi\n'
                            f'Kredi satın almak için uygulamayı açın.')
            return False

        profil = EmlakciProfil.query.filter_by(user_id=user.id).first()
        if not profil:
            frontend_url = current_app.config.get('FRONTEND_URL', '')
            wa.mesaj_gonder(pid, tok, telefon,
                            f'⚠️ Önce emlakçı profilinizi tamamlayın:\n🔗 {frontend_url}/emlak-profil')
            return False

        try:
            pdf_bytes = pdf_olustur(session, profil)
        except Exception as e:
            logger.error(f'[Emlak] PDF hatası: {e}', exc_info=True)
            wa.mesaj_gonder(pid, tok, telefon, '❌ Belge oluşturulurken hata oluştu. Lütfen tekrar deneyin.')
            return False

        token   = kaydet(pdf_bytes)
        base_url = current_app.config.get('BASE_URL', '').rstrip('/')
        pdf_url  = f'{base_url}/api/belge/{token}'

        # Kayıt
        try:
            alici     = session.get('alici', {})
            tasinmaz  = session.get('tasinmaz', {})
            konum     = session.get('konum') or {}
            yg = YerGosterme(
                user_id=user.id,
                alici_ad_soyad=alici.get('ad_soyad') or alici.get('ad', ''),
                alici_adres=alici.get('adres'),
                alici_tc_no=alici.get('tc_no'),
                alici_telefon=alici.get('telefon'),
                tasinmaz_sehir=tasinmaz.get('sehir'),
                tasinmaz_ilce=tasinmaz.get('ilce'),
                tasinmaz_mahalle=tasinmaz.get('mahalle'),
                tasinmaz_ada=tasinmaz.get('ada'),
                tasinmaz_parsel=tasinmaz.get('parsel'),
                tasinmaz_adres=tasinmaz.get('adres') or konum.get('adres'),
                tasinmaz_alan=str(tasinmaz.get('alan_m2', '')),
                konum_lat=konum.get('lat'),
                konum_lng=konum.get('lng'),
                islem_turu=session.get('islem_turu'),
                fiyat=session.get('fiyat'),
                komisyon_kira_ay=session.get('komisyon_kira_ay'),
                komisyon_satis_yuzde=session.get('komisyon_satis_yuzde'),
                sablon_no=session.get('sablon_no', 1),
                fotografli_mi=session.get('fotografli_mi', True),
                pdf_token=token,
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

        alici_adi = (session.get('alici', {}).get('ad_soyad') or
                     session.get('alici', {}).get('ad', 'Alıcı'))
        wa.belge_gonder(pid, tok, telefon, pdf_url,
                        f'yer_gosterme_{date.today().strftime("%Y%m%d")}.pdf',
                        f'✅ {alici_adi} için Yer Gösterme Sözleşmesi hazır!')
        logger.info(f'[Emlak] Belge gönderildi → {telefon}')
        return True

    # ── MESAJ METİNLERİ ──────────────────────────────────────────────────────

    def _menu_metni(self) -> str:
        return (
            '🏠 *Yer Gösterme Sözleşmesi*\n\n'
            'Şablon seçin:\n'
            '1️⃣  Klasik (resmi, sade)\n'
            '2️⃣  Modern (koyu başlık)\n'
            '3️⃣  Minimalist (açık gri)\n\n'
            '1, 2 veya 3 yazın.'
        )

    def _foto_secim_metni(self) -> str:
        return (
            '📸 *Fotoğraf*\n\n'
            'Sözleşmeye mülk fotoğrafı eklensin mi?\n\n'
            '*E* → Evet, fotoğraf ekle (1-4 adet)\n'
            '*H* → Hayır, fotoğrafsız devam et'
        )

    def _islem_turu_metni(self) -> str:
        return (
            '🔑 *İşlem Türü*\n\n'
            '*K* → Kiralama\n'
            '*S* → Satış'
        )

    def _alici_metni(self) -> str:
        return (
            '👤 *Alıcı / Kiracı Adayı*\n\n'
            'Aşağıdakilerden birini yapın:\n\n'
            '• Rehberden *kişi kartı* gönderin\n'
            '• Veya yazın: *Ad Soyad, TC No, Telefon*\n\n'
            '_Örnek: Ali Veli, 12345678901, 0532 111 2222_\n'
            '_TC ve telefon opsiyoneldir._'
        )

    def _tasinmaz_metni(self) -> str:
        return (
            '🏡 *Taşınmaz Bilgisi*\n\n'
            '• 📍 *Konum paylaşın* (en doğru yöntem)\n'
            '• Veya *adres yazın*\n\n'
            '_Örnek: Kadıköy, Moda Cad. No:5, Daire 3_'
        )

    def _fiyat_metni(self, islem_turu: str) -> str:
        birim = 'aylık kira' if islem_turu == 'kira' else 'satış'
        return (
            f'💰 *{birim.capitalize()} Bedeli*\n\n'
            f'Taşınmazın {birim} bedelini TL olarak yazın.\n\n'
            '_Örnek: 15000_'
        )

    def _komisyon_metni(self, session: dict) -> str:
        if session['islem_turu'] == 'kira':
            return (
                '📋 *Komisyon (Kiralama)*\n\n'
                'Kaç aylık kira komisyonu alıyorsunuz?\n\n'
                '_Örnek: 1_\n'
                '_Atlamak için: atla_'
            )
        else:
            return (
                '📋 *Komisyon (Satış)*\n\n'
                'Satış bedeli üzerinden komisyon oranı (%)?\n\n'
                '_Örnek: 2_\n'
                '_Atlamak için: atla_'
            )

    def _foto_metni(self) -> str:
        return (
            f'📸 *Fotoğraflar* (1-{self.MAX_FOTOGRAF} adet)\n\n'
            'Mülk fotoğraflarını gönderin.\n'
            'Bitince *tamam* yazın.'
        )

    def _onay_metni(self, session: dict) -> str:
        alici    = session.get('alici', {})
        tasinmaz = session.get('tasinmaz', {})
        konum    = session.get('konum') or {}
        sablon_adlari = {1: 'Klasik', 2: 'Modern', 3: 'Minimalist'}
        islem_tr = 'Kiralama' if session.get('islem_turu') == 'kira' else 'Satış'
        adres    = tasinmaz.get('adres') or konum.get('adres') or '-'
        alici_ad = alici.get('ad_soyad') or alici.get('ad') or '-'
        tc       = alici.get('tc_no') or '-'
        tel      = alici.get('telefon') or '-'
        foto_say = len(session.get('fotograflar', []))
        komisyon = ''
        if session.get('islem_turu') == 'kira':
            k = session.get('komisyon_kira_ay', '?')
            komisyon = f'{k} aylık'
        else:
            k = session.get('komisyon_satis_yuzde', '?')
            komisyon = f'%{k}'

        return (
            f'📋 *Özet — Onaylıyor musunuz?*\n\n'
            f'🖨 Şablon: {sablon_adlari.get(session.get("sablon_no", 1))}\n'
            f'📸 Fotoğraf: {"Var (" + str(foto_say) + " adet)" if session.get("fotografli_mi") else "Yok"}\n'
            f'🔑 İşlem: {islem_tr}\n'
            f'👤 Alıcı: {alici_ad}\n'
            f'🪪 TC: {tc}\n'
            f'📞 Tel: {tel}\n'
            f'📍 Adres: {adres[:80]}{"..." if len(adres) > 80 else ""}\n'
            f'💰 Bedel: {session.get("fiyat", "-")} TL\n'
            f'📊 Komisyon: {komisyon}\n\n'
            '✅ *evet* → Belgeyi oluştur\n'
            '✏️ Düzeltmek için: *alıcı*, *taşınmaz*, *fiyat*\n'
            '❌ *iptal* → Sıfırla'
        )
