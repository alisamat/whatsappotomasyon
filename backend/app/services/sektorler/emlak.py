"""
EMLAK SEKTÖRÜ — Yer Gösterme Sözleşmesi
Sadeleştirilmiş 3-adım akış: hosgeldin → veri_toplama → onay_bekleniyor
"""
import logging
from datetime import date
from app.services.sektorler.base import BaseSektorHandler
from app.services import whatsapp_client as wa

logger = logging.getLogger(__name__)


def yeni_session() -> dict:
    return {
        'adim': 'hosgeldin',
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
        ml       = metin.lower()

        # Global komutlar
        if ml in ('iptal', 'sıfırla', 'reset', 'yeni', '0'):
            session.update(yeni_session())
            wa.mesaj_gonder(phone_number_id, access_token, telefon,
                            '🔄 Sıfırlandı.\n\n' + self._hosgeldin_metni())
            return False

        if ml in ('durum', 'bakiye', 'kredi'):
            wa.mesaj_gonder(phone_number_id, access_token, telefon,
                            f'💳 Kredi bakiyeniz: {user.kredi:.0f}')
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
                telefon, metin, session, phone_number_id, access_token, user)
        else:
            session['adim'] = 'hosgeldin'
            wa.mesaj_gonder(phone_number_id, access_token, telefon, self._hosgeldin_metni())
            return False

    # ── ADIM: hosgeldin ───────────────────────────────────────────────────────────

    def _isle_hosgeldin(self, telefon, mesaj, msg_type, metin, session, pid, tok, user):
        wa.mesaj_gonder(pid, tok, telefon, self._hosgeldin_metni())
        session['adim'] = 'veri_toplama'

        # Eğer ilk mesajda veri varsa hemen işle
        if msg_type in ('image', 'location', 'contacts') or (msg_type == 'text' and len(metin) > 8):
            self._veri_isle(telefon, mesaj, msg_type, metin, session, pid, tok)
            if self.session_tamam_mi(session):
                session['adim'] = 'onay_bekleniyor'
                wa.mesaj_gonder(pid, tok, telefon, self._onay_metni(session))
        return False

    # ── ADIM: veri_toplama ────────────────────────────────────────────────────────

    def _isle_veri_toplama(self, telefon, mesaj, msg_type, metin, session, pid, tok, user):
        ml = metin.lower()

        # Link isteği (yöntem 2)
        if ml in ('2', 'link', 'form', 'bağlantı', 'baglanty', 'web'):
            self._link_gonder(telefon, session, pid, tok, user)
            return False

        # Şablon değiştirme
        sablon_map = {
            '1': 1, 'klasik': 1, 'şablon 1': 1, 'sablon 1': 1,
            '2': 2, 'modern': 2, 'şablon 2': 2, 'sablon 2': 2,
            '3': 3, 'minimalist': 3, 'şablon 3': 3, 'sablon 3': 3,
        }
        if ml in sablon_map:
            session['sablon_no'] = sablon_map[ml]
            isimler = {1: 'Klasik', 2: 'Modern', 3: 'Minimalist'}
            wa.mesaj_gonder(pid, tok, telefon,
                            f'🖨 Şablon: *{isimler[sablon_map[ml]]}* seçildi.')
            return False

        # Veriyi işle
        self._veri_isle(telefon, mesaj, msg_type, metin, session, pid, tok)

        # Tüm zorunlu alanlar doluysa onaya geç
        if self.session_tamam_mi(session):
            session['adim'] = 'onay_bekleniyor'
            wa.mesaj_gonder(pid, tok, telefon, self._onay_metni(session))

        return False

    # ── ADIM: onay_bekleniyor ─────────────────────────────────────────────────────

    def _isle_onay(self, telefon, metin, session, pid, tok, user):
        ml = metin.lower().strip()
        if ml in ('evet', 'onayla', 'onay', 'ok', 'tamam', 'e', 'y', 'yes'):
            return self._belge_uret(telefon, session, pid, tok, user)
        elif ml in ('alici', 'alıcı', 'isim', 'ad', 'müşteri'):
            session['alici']['ad_soyad'] = None
            session['adim'] = 'veri_toplama'
            wa.mesaj_gonder(pid, tok, telefon,
                            '👤 Alıcı adını tekrar girin\n'
                            '_(rehberden kişi kartı veya yazarak)_')
        elif ml in ('adres', 'tasinmaz', 'taşınmaz', 'konum', 'yer'):
            session['tasinmaz']['adres'] = None
            session['konum'] = None
            session['adim'] = 'veri_toplama'
            wa.mesaj_gonder(pid, tok, telefon,
                            '📍 Adresi veya konumu tekrar gönderin:')
        elif ml in ('fiyat', 'bedel', 'ücret', 'ucret'):
            session['fiyat'] = None
            session['adim'] = 'veri_toplama'
            wa.mesaj_gonder(pid, tok, telefon,
                            '💰 Fiyatı (TL olarak) tekrar girin:')
        elif ml in ('tur', 'tür', 'islem', 'işlem', 'kira', 'kiralık', 'satış', 'satilık'):
            session['islem_turu'] = None
            session['adim'] = 'veri_toplama'
            wa.mesaj_gonder(pid, tok, telefon,
                            '🔑 İşlem türünü yazın: *kiralık* veya *satılık*')
        else:
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

            if bilgi.get('komisyon_ay') and not session['komisyon_kira_ay']:
                session['komisyon_kira_ay'] = bilgi['komisyon_ay']
            if bilgi.get('komisyon_yuzde') and not session['komisyon_satis_yuzde']:
                session['komisyon_satis_yuzde'] = bilgi['komisyon_yuzde']

        # Güncelleme özeti + kalan eksikler
        if guncellendi:
            eksik = self._eksik_alanlar(session)
            satir = '✅ ' + ' · '.join(guncellendi)
            if eksik:
                satir += '\n\n📝 Eksik: ' + ' · '.join(eksik)
            wa.mesaj_gonder(pid, tok, telefon, satir)
        else:
            # Hiçbir şey anlaşılmadıysa ne eksik olduğunu hatırlat
            eksik = self._eksik_alanlar(session)
            if eksik:
                wa.mesaj_gonder(pid, tok, telefon,
                                '🤔 Anlaşılamadı.\n\n📝 Eksik: ' + ' · '.join(eksik))

    def _eksik_alanlar(self, session) -> list:
        eksik = []
        if not session.get('alici', {}).get('ad_soyad'):
            eksik.append('alıcı adı')
        if not (session.get('tasinmaz', {}).get('adres') or session.get('konum')):
            eksik.append('adres/konum')
        if not session.get('islem_turu'):
            eksik.append('kiralık/satılık')
        if not session.get('fiyat'):
            eksik.append('fiyat (TL)')
        return eksik

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

        if not kayit.kredi_dus(user, self.KREDI_MALIYETI):
            wa.mesaj_gonder(pid, tok, telefon,
                            f'❌ Yetersiz kredi. Belge için {self.KREDI_MALIYETI} kredi gerekli.\n'
                            f'💳 Bakiye: {user.kredi:.0f} kredi')
            return False

        profil = EmlakciProfil.query.filter_by(user_id=user.id).first()
        if not profil:
            frontend_url = current_app.config.get('FRONTEND_URL', '')
            wa.mesaj_gonder(pid, tok, telefon,
                            f'⚠️ Önce emlakçı profilinizi tamamlayın:\n'
                            f'🔗 {frontend_url}/emlak-profil')
            return False

        try:
            pdf_bytes = pdf_olustur(session, profil)
        except Exception as e:
            logger.error(f'[Emlak] PDF hatası: {e}', exc_info=True)
            wa.mesaj_gonder(pid, tok, telefon,
                            '❌ PDF oluşturulurken hata oluştu. Tekrar deneyin.')
            return False

        token_str = kaydet(pdf_bytes)
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

        alici_adi = session.get('alici', {}).get('ad_soyad', 'Alıcı')
        wa.belge_gonder(pid, tok, telefon, pdf_url,
                        f'yer_gosterme_{date.today().strftime("%Y%m%d")}.pdf',
                        f'✅ {alici_adi} için Yer Gösterme Sözleşmesi hazır!')
        logger.info(f'[Emlak] Belge gönderildi → {telefon}')
        return True

    # ── MESAJ METİNLERİ ─────────────────────────────────────────────────────────

    def _hosgeldin_metni(self) -> str:
        return (
            '🏠 *Yer Gösterme Sözleşmesi*\n\n'
            'Belgeyi 3 şekilde oluşturabilirsiniz:\n\n'
            '📱 *1 — WhatsApp ile (sıra önemli değil)*\n'
            '· 👤 Rehberden *kişi kartı* gönderin\n'
            '· 📍 *Konum* paylaşın veya adres yazın\n'
            '· 💬 İşlem ve fiyat: _"kiralık 15000"_\n'
            '· 📸 Fotoğraf isteğe bağlı (max 4)\n\n'
            '🔗 *2 — Web formu*\n'
            '"link" yazın → formu doldurun → PDF gelir\n\n'
            '✍️ *3 — Tek mesajda serbest yaz*\n'
            '_"Ali Veli 05321112222 Kadıköy Moda Cad 5_\n'
            '_kiralık 18.000 TL komisyon 1 ay"_\n\n'
            '─────────────────\n'
            '_Şablon:_ 1 klasik · 2 modern · 3 minimalist\n'
            '_Sıfırlamak için:_ sıfırla'
        )

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
            komisyon = f'{k} aylık kira' if k else '—'
        elif session.get('islem_turu') == 'satis':
            k = session.get('komisyon_satis_yuzde')
            komisyon = f'%{k}' if k else '—'

        return (
            '📋 *Özet — Onaylıyor musunuz?*\n\n'
            f'🖨 Şablon : {sablon_adlari.get(session.get("sablon_no", 1))}\n'
            f'📸 Fotoğraf: {"Var (" + str(foto) + " adet)" if foto > 0 else "Yok"}\n'
            f'🔑 İşlem   : {islem_tr}\n'
            f'👤 Alıcı   : {alici_ad}\n'
            f'🪪 TC      : {tc}\n'
            f'📞 Tel     : {tel}\n'
            f'📍 Adres   : {adres[:80]}{"..." if len(adres) > 80 else ""}\n'
            f'💰 Bedel   : {session.get("fiyat", "—")} TL\n'
            f'📊 Komisyon: {komisyon}\n\n'
            '✅ *evet* → Belgeyi oluştur\n'
            '✏️ Düzelt → *alıcı* · *adres* · *fiyat* · *tür*\n'
            '❌ *sıfırla* → Baştan başla'
        )
