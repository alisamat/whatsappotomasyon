"""
EMLAK PDF — Taşınmaz Yer Gösterme Sözleşmesi
3 şablon: Klasik (1), Modern (2), Minimalist (3)
"""
import io
import logging
from datetime import date

logger = logging.getLogger(__name__)


def pdf_olustur(session: dict, profil, yer_gosterme_id: int = 0) -> bytes:
    sablon = session.get('sablon_no', 1)
    if sablon == 2:
        return _uret(session, profil, yer_gosterme_id, stil='modern')
    elif sablon == 3:
        return _uret(session, profil, yer_gosterme_id, stil='minimalist')
    return _uret(session, profil, yer_gosterme_id, stil='klasik')


def _uret(session: dict, profil, yer_gosterme_id: int, stil: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle, HRFlowable, PageBreak, Image as RLImage)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import requests as _req

    W, H = A4
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    # ── Renkler ──
    if stil == 'modern':
        header_bg   = colors.HexColor('#0f172a')
        header_fg   = colors.white
        accent      = colors.HexColor('#25D366')
        label_bg    = colors.HexColor('#1e293b')
        label_fg    = colors.white
        row_bg      = colors.HexColor('#f8fafc')
    elif stil == 'minimalist':
        header_bg   = colors.HexColor('#f1f5f9')
        header_fg   = colors.HexColor('#0f172a')
        accent      = colors.HexColor('#475569')
        label_bg    = colors.HexColor('#f1f5f9')
        label_fg    = colors.HexColor('#374151')
        row_bg      = colors.white
    else:  # klasik
        header_bg   = colors.white
        header_fg   = colors.HexColor('#0f172a')
        accent      = colors.HexColor('#0f172a')
        label_bg    = colors.HexColor('#f1f5f9')
        label_fg    = colors.HexColor('#374151')
        row_bg      = colors.white

    styles = getSampleStyleSheet()
    baslik_stil = ParagraphStyle('baslik', parent=styles['Normal'],
                                 fontSize=15 if stil != 'modern' else 16,
                                 fontName='Helvetica-Bold',
                                 textColor=header_fg if stil == 'modern' else header_fg,
                                 alignment=1, spaceAfter=4)
    alt_baslik_stil = ParagraphStyle('altbaslik', parent=styles['Normal'],
                                     fontSize=9, textColor=colors.HexColor('#64748b'),
                                     alignment=1, spaceAfter=2)
    madde_stil = ParagraphStyle('madde', parent=styles['Normal'],
                                fontSize=9, fontName='Helvetica-Bold',
                                textColor=accent, spaceBefore=10, spaceAfter=4)
    normal_stil = ParagraphStyle('normal', parent=styles['Normal'],
                                 fontSize=8.5, leading=13, spaceAfter=4)
    kucuk_stil  = ParagraphStyle('kucuk', parent=styles['Normal'],
                                 fontSize=7.5, leading=12, textColor=colors.HexColor('#475569'))

    alici   = session.get('alici', {})
    konum   = session.get('konum', {})
    tasinmaz = session.get('tasinmaz', {})
    islem_turu = session.get('islem_turu', 'kira')
    fiyat   = session.get('fiyat', '-')
    komisyon_kira_ay  = session.get('komisyon_kira_ay', getattr(profil, 'komisyon_kira_ay', 1) if profil else 1)
    komisyon_satis_yuz = session.get('komisyon_satis_yuzde', getattr(profil, 'komisyon_satis_yuzde', 2.0) if profil else 2.0)
    bugun   = date.today().strftime('%d.%m.%Y')
    sozno   = f'YGS-{date.today().strftime("%Y%m%d")}-{yer_gosterme_id or "NEW"}'

    tasinmaz_adres = (tasinmaz.get('adres') or konum.get('adres') or '-')
    tasinmaz_sehir = tasinmaz.get('sehir') or '-'
    tasinmaz_ilce  = tasinmaz.get('ilce') or '-'
    tasinmaz_mah   = tasinmaz.get('mahalle') or '-'
    tasinmaz_ada   = tasinmaz.get('ada') or '-'
    tasinmaz_parsel = tasinmaz.get('parsel') or '-'
    tasinmaz_alan  = tasinmaz.get('alan_m2') or '-'

    hikaye = []

    # ── BAŞLIK ──
    if stil == 'modern':
        header_data = [[Paragraph('TAŞINMAZ YER GÖSTERME SÖZLEŞMESİ', baslik_stil)],
                       [Paragraph(f'Sözleşme No: {sozno}  ·  Tarih: {bugun}', alt_baslik_stil)]]
        header_tablo = Table(header_data, colWidths=[W - 4*cm])
        header_tablo.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), header_bg),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 16),
        ]))
        hikaye.append(header_tablo)
    else:
        hikaye.append(Paragraph('TAŞINMAZ YER GÖSTERME SÖZLEŞMESİ', baslik_stil))
        hikaye.append(Paragraph(f'Sözleşme No: {sozno}  ·  Tarih: {bugun}', alt_baslik_stil))
        hikaye.append(HRFlowable(width='100%', thickness=1.5, color=accent, spaceAfter=8))

    def tablo_olustur(veriler):
        t = Table(veriler, colWidths=[4.5*cm, 12*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (0, -1), label_bg),
            ('TEXTCOLOR',    (0, 0), (0, -1), label_fg),
            ('BACKGROUND',   (1, 0), (1, -1), row_bg),
            ('FONTNAME',     (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE',     (0, 0), (-1, -1), 8.5),
            ('GRID',         (0, 0), (-1, -1), 0.3, colors.HexColor('#e2e8f0')),
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',   (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
            ('LEFTPADDING',  (0, 0), (-1, -1), 8),
            ('FONTNAME',     (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        return t

    # ── MADDE 1: TARAFLAR ──
    hikaye.append(Paragraph('MADDE 1 — TARAFLAR', madde_stil))
    hikaye.append(Paragraph('1.1 Sorumlu Emlak Danışmanı', normal_stil))
    profil_ad     = getattr(profil, 'ad_soyad', '-') if profil else '-'
    profil_isletme = getattr(profil, 'isletme_adi', '') if profil else ''
    profil_adres  = getattr(profil, 'is_adresi', '-') if profil else '-'
    profil_tel    = getattr(profil, 'telefon', '-') if profil else '-'
    profil_lisans = getattr(profil, 'lisans_no', '-') if profil else '-'
    hikaye.append(tablo_olustur([
        ['Ad Soyad', profil_ad],
        ['İşletme Adı', profil_isletme or '-'],
        ['İş Adresi', profil_adres or '-'],
        ['Telefon', profil_tel or '-'],
        ['Yetki Belgesi No', profil_lisans or '-'],
    ]))
    hikaye.append(Spacer(1, 0.3*cm))
    hikaye.append(Paragraph('1.2 Kiracı Adayı / Alıcı Adayı', normal_stil))
    tc_gizli = ''
    tc = alici.get('tc_no', '') or ''
    if tc and len(tc) >= 7:
        tc_gizli = tc[:3] + '****' + tc[-4:]
    else:
        tc_gizli = tc or '-'
    hikaye.append(tablo_olustur([
        ['Ad Soyad / Unvan', alici.get('ad_soyad') or alici.get('ad', '-') or '-'],
        ['TC Kimlik / Vergi No', tc or '-'],
        ['Tebligat Adresi', alici.get('adres') or '-'],
        ['İletişim', alici.get('telefon') or '-'],
    ]))

    # ── MADDE 2: SÖZLEŞME KONUSU ──
    hikaye.append(Paragraph('MADDE 2 — SÖZLEŞMENİN KONUSU', madde_stil))
    islem_tr = 'kiralanması' if islem_turu == 'kira' else 'satılması'
    islem_tr2 = 'kiralama' if islem_turu == 'kira' else 'satın alma'
    hikaye.append(Paragraph(
        f'2.1 Sorumlu Emlak Danışmanı, üstlendiği taşınmazın {islem_tr} sözleşmesinin yapılması imkanını '
        f'hazırlama görevi çerçevesinde; aşağıda bilgileri verilen taşınmazı {islem_tr2} amacıyla '
        f'Kiracı Adayı/Alıcı Adayına gösterdiğini kabul ve taahhüt eder.',
        normal_stil
    ))
    hikaye.append(Spacer(1, 0.2*cm))
    hikaye.append(Paragraph('2.2 Taşınmaz Bilgileri', normal_stil))
    hikaye.append(tablo_olustur([
        ['İl', tasinmaz_sehir],
        ['İlçe', tasinmaz_ilce],
        ['Mahalle/Köy', tasinmaz_mah],
        ['Ada / Parsel', f'{tasinmaz_ada} / {tasinmaz_parsel}'],
        ['Adres', tasinmaz_adres],
        ['Yüzölçümü', f'{tasinmaz_alan} m²' if tasinmaz_alan != '-' else '-'],
        ['Kira/Satış Bedeli', f'{fiyat} TL' if fiyat != '-' else '-'],
    ]))
    if konum.get('lat') and konum.get('lng'):
        hikaye.append(Paragraph(
            f'📍 Google Maps: {konum.get("google_maps", "")}', kucuk_stil
        ))

    # ── MADDE 3: KOMİSYON ──
    hikaye.append(Paragraph('MADDE 3 — TARAFLARın HAK VE YÜKÜMLÜLÜKLERİ', madde_stil))
    if islem_turu == 'kira':
        komisyon_text = (
            f'3.1 Kiracı Adayı, Sorumlu Emlak Danışmanını devre dışı bırakarak işlem '
            f'gerçekleştirdiği takdirde aylık kira bedelinin {komisyon_kira_ay} (bir) katı '
            f'tutarında komisyon bedeli +KDV ödeyeceğini kabul eder.'
        )
    else:
        komisyon_text = (
            f'3.1 Alıcı Adayı, Sorumlu Emlak Danışmanını devre dışı bırakarak işlem '
            f'gerçekleştirdiği takdirde satış bedelinin %{komisyon_satis_yuz} tutarında '
            f'komisyon bedeli +KDV ödeyeceğini kabul eder.'
        )
    hikaye.append(Paragraph(komisyon_text, normal_stil))
    hikaye.append(Paragraph(
        '3.2 İş bu sözleşmede belirtilen taşınmaz gayrimenkul kiralanmadığı/satılmadığı takdirde GEÇERSİZDİR.',
        normal_stil
    ))

    # ── MADDE 4: KVKK ──
    hikaye.append(Paragraph('MADDE 4 — GİZLİLİK VE KİŞİSEL VERİLERİN KORUNMASI', madde_stil))
    hikaye.append(Paragraph(
        'Sorumlu Emlak Danışmanı ile paylaşılan kişisel veriler, 6698 Sayılı Kişisel Verilerin '
        'Korunması Kanunu (KVKK) kapsamında işlenmektedir. Kiracı Adayı/Alıcı Adayı, kanunda '
        'öngörülen tedbirler kapsamında kişisel verilerinin işlenmesine açık rızasının bulunduğunu kabul eder.',
        normal_stil
    ))

    # ── MADDE 5: YETKİLİ MAHKEME ──
    yetki_sehri = getattr(profil, 'yetki_sehri', 'İstanbul') if profil else 'İstanbul'
    hikaye.append(Paragraph('MADDE 5 — İHTİLAFLARIN HALLİ', madde_stil))
    hikaye.append(Paragraph(
        f'Taraflar arasında çıkacak uyuşmazlıklarda {yetki_sehri} Mahkemeleri ve '
        f'İcra Müdürlükleri münhasıran yetkili kılınmıştır.',
        normal_stil
    ))

    # ── MADDE 6: YÜRÜRLÜK ──
    hikaye.append(Paragraph('MADDE 6 — YÜRÜRLÜK', madde_stil))
    hikaye.append(Paragraph(
        f'İşbu sözleşme taraflarca imzalandığı tarihte yürürlüğe girer. '
        f'İşbu 6 (altı) madde ve 1 (bir) sayfadan oluşan sözleşme, '
        f'{bugun} tarihinde iki suret olarak düzenlenmiştir.',
        normal_stil
    ))

    # ── İMZA ──
    hikaye.append(Spacer(1, 0.8*cm))
    hikaye.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0')))
    hikaye.append(Spacer(1, 0.5*cm))
    imza_data = [
        [Paragraph('<b>KİRACI ADAYI / ALICI ADAYI</b>', normal_stil),
         Paragraph('<b>SORUMLU EMLAK DANIŞMANI</b>', normal_stil)],
        ['', ''],
        ['', ''],
        [Paragraph('_________________________', normal_stil),
         Paragraph('_________________________', normal_stil)],
        [Paragraph(alici.get('ad_soyad') or alici.get('ad', ''), kucuk_stil),
         Paragraph(profil_ad, kucuk_stil)],
    ]
    imza_tablo = Table(imza_data, colWidths=[(W - 4*cm) / 2, (W - 4*cm) / 2])
    imza_tablo.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    hikaye.append(imza_tablo)

    # ── FOTOĞRAFLAR (ayrı sayfa) ──
    if session.get('fotografli_mi', True) and session.get('fotograflar'):
        hikaye.append(PageBreak())
        foto_baslik = ParagraphStyle('fotobaslik', parent=styles['Normal'],
                                     fontSize=13, fontName='Helvetica-Bold',
                                     textColor=accent, alignment=1, spaceAfter=16)
        hikaye.append(Paragraph('MÜLKE AİT FOTOĞRAFLAR', foto_baslik))
        hikaye.append(HRFlowable(width='100%', thickness=1, color=accent, spaceAfter=12))

        fotograflar = session['fotograflar'][:4]
        foto_caption = ParagraphStyle('fotocaption', parent=styles['Normal'],
                                      fontSize=8, textColor=colors.HexColor('#64748b'),
                                      alignment=1, spaceAfter=8)
        # 2 foto per row
        for i in range(0, len(fotograflar), 2):
            row = []
            for j in range(2):
                idx = i + j
                if idx < len(fotograflar):
                    try:
                        foto = fotograflar[idx]
                        img_buf = io.BytesIO(foto if isinstance(foto, bytes) else b'')
                        rl_img = RLImage(img_buf, width=7.5*cm, height=5.5*cm)
                        row.append([rl_img, Paragraph(f'Fotoğraf {idx + 1}', foto_caption)])
                    except Exception as e:
                        logger.warning(f'[EmlakPDF] Foto {idx+1} eklenemedi: {e}')
                        row.append(['', ''])
                else:
                    row.append(['', ''])
            foto_tablo = Table(
                [[row[0][0], row[1][0]],
                 [row[0][1], row[1][1]]],
                colWidths=[(W - 4*cm) / 2, (W - 4*cm) / 2]
            )
            foto_tablo.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            hikaye.append(foto_tablo)
            hikaye.append(Spacer(1, 0.3*cm))

    doc.build(hikaye)
    return buf.getvalue()
