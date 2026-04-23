"""
EMLAK SEKTÖRÜ — Yer Gösterme Belgesi PDF üretimi
Akış:
  1. Emlakçı 1-3 fotoğraf gönderir
  2. Konum paylaşır
  3. Alıcı kişi bilgisi gönderir (rehberden kişi kartı)
  4. Sistem PDF üretir → geri gönderir, 5 kredi düşer
"""
import io
import logging
from datetime import datetime
from app.services.sektorler.base import BaseSektorHandler
from app.services import whatsapp_client as wa

logger = logging.getLogger(__name__)


class EmlakHandler(BaseSektorHandler):
    SEKTOR_KODU    = 'emlak'
    KREDI_MALIYETI = 5
    MIN_FOTOGRAF   = 1
    MAX_FOTOGRAF   = 4

    def session_tamam_mi(self, session: dict) -> bool:
        return (
            len(session.get('fotograflar', [])) >= self.MIN_FOTOGRAF and
            session.get('konum') is not None and
            session.get('alici') is not None
        )

    def beklenen_veri_mesaji(self) -> str:
        return (
            '🏠 *Yer Gösterme Belgesi* için şunları gönderin:\n\n'
            '📸 1-3 mülk fotoğrafı\n'
            '📍 Konum (konum paylaş)\n'
            '👤 Alıcı bilgisi (rehberden kişi paylaş)\n\n'
            'Hepsini gönderdikten sonra belge otomatik oluşturulacak.'
        )

    def handle(self, telefon: str, session: dict,
               phone_number_id: str, access_token: str) -> bool:
        if not self.session_tamam_mi(session):
            eksik = self._eksik_listesi(session)
            wa.mesaj_gonder(
                phone_number_id, access_token, telefon,
                f'📋 Belge için şunlar eksik:\n{eksik}\n\nGönderdikçe belge oluşturulacak.'
            )
            return False

        # PDF oluştur
        try:
            pdf_bytes = self._pdf_olustur(session)
        except Exception as e:
            logger.error(f'[Emlak] PDF hatası: {e}')
            wa.mesaj_gonder(phone_number_id, access_token, telefon,
                            '❌ Belge oluşturulurken hata oluştu. Lütfen tekrar deneyin.')
            return False

        # PDF'i geçici olarak bir URL'ye yükle (ileride S3/Cloudinary entegrasyonu)
        # Şimdilik dosyayı kaydet ve URL döndür (placeholder)
        pdf_url = self._pdf_yukle(pdf_bytes, telefon)
        if not pdf_url:
            wa.mesaj_gonder(phone_number_id, access_token, telefon,
                            '❌ Belge yüklenemedi. Lütfen tekrar deneyin.')
            return False

        alici_adi = session.get('alici', {}).get('ad', 'Alıcı')
        wa.belge_gonder(
            phone_number_id, access_token, telefon,
            pdf_url,
            f'yer_gosterme_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            f'✅ {alici_adi} için Yer Gösterme Belgesi hazır!'
        )
        logger.info(f'[Emlak] Belge gönderildi → {telefon}')
        return True

    # ── Yardımcı metodlar ──────────────────────────────────────────

    def _eksik_listesi(self, session: dict) -> str:
        satirlar = []
        if not session.get('fotograflar'):
            satirlar.append('📸 Fotoğraf (en az 1)')
        if not session.get('konum'):
            satirlar.append('📍 Konum')
        if not session.get('alici'):
            satirlar.append('👤 Alıcı kişi bilgisi')
        return '\n'.join(f'• {s}' for s in satirlar)

    def _pdf_olustur(self, session: dict) -> bytes:
        """ReportLab ile Yer Gösterme Belgesi PDF üret."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import io as _io
        import requests as _req

        buf = _io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        baslik_stil = ParagraphStyle('baslik', parent=styles['Title'],
                                     fontSize=16, spaceAfter=12, alignment=1)
        normal_stil = ParagraphStyle('normal', parent=styles['Normal'],
                                     fontSize=11, spaceAfter=6)

        konum = session.get('konum', {})
        alici = session.get('alici', {})
        tarih = datetime.now().strftime('%d.%m.%Y %H:%M')

        hikaye = []
        hikaye.append(Paragraph('YER GÖSTERME BELGESİ', baslik_stil))
        hikaye.append(Spacer(1, 0.5*cm))

        tablo_verisi = [
            ['Tarih', tarih],
            ['Alıcı Adı', alici.get('ad', '-')],
            ['Alıcı Telefon', alici.get('telefon', '-')],
            ['Konum Adı', konum.get('ad', '-')],
            ['Adres', konum.get('adres', '-')],
            ['Google Maps', konum.get('google_maps', '-')],
        ]
        tablo = Table(tablo_verisi, colWidths=[4*cm, 13*cm])
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE',   (0, 0), (-1, -1), 10),
            ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING',    (0, 0), (-1, -1), 6),
        ]))
        hikaye.append(tablo)
        hikaye.append(Spacer(1, 0.5*cm))

        # Fotoğraflar (bytes olarak saklanıyor)
        for idx, foto in enumerate(session.get('fotograflar', [])[:3], 1):
            try:
                if isinstance(foto, bytes):
                    img_buf = _io.BytesIO(foto)
                else:
                    r = _req.get(foto, timeout=15)
                    img_buf = _io.BytesIO(r.content)
                rl_img = RLImage(img_buf, width=14*cm, height=9*cm)
                rl_img.hAlign = 'CENTER'
                hikaye.append(Paragraph(f'Fotoğraf {idx}', normal_stil))
                hikaye.append(rl_img)
                hikaye.append(Spacer(1, 0.3*cm))
            except Exception as e:
                logger.warning(f'[Emlak] Fotoğraf eklenemedi: {e}')

        hikaye.append(Spacer(1, 1*cm))
        hikaye.append(Paragraph(
            'Bu belge, yer gösterme hizmetinin gerçekleştirildiğini teyit eder.',
            normal_stil
        ))

        doc.build(hikaye)
        return buf.getvalue()

    def _pdf_yukle(self, pdf_bytes: bytes, telefon: str) -> str | None:
        """PDF'i belge_store'a kaydet ve Railway URL'ini döndür."""
        try:
            from flask import current_app
            from app.services.belge_store import kaydet
            token = kaydet(pdf_bytes)
            base_url = current_app.config.get('BASE_URL', '').rstrip('/')
            return f'{base_url}/api/belge/{token}'
        except Exception as e:
            logger.error(f'[Emlak] PDF yükleme hatası: {e}')
            return None
