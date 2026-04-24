"""
VERİ MODELLERİ
"""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ── Kullanıcı (işletme sahibi) ────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    ad_soyad      = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    telefon       = db.Column(db.String(20), unique=True, nullable=False)  # WhatsApp numarası
    sifre_hash    = db.Column(db.String(256), nullable=False)
    sektor        = db.Column(db.String(50), nullable=False)  # emlak, marangoz, ...
    kredi         = db.Column(db.Float, default=0.0)
    paket_bitis   = db.Column(db.DateTime, nullable=True)      # Abonelik bitiş tarihi
    aktif         = db.Column(db.Boolean, default=True)
    kayit_tarihi  = db.Column(db.DateTime, default=datetime.utcnow)
    son_islem     = db.Column(db.DateTime, nullable=True)

    islemler      = db.relationship('IslemLog', backref='user', lazy=True)
    odemeler      = db.relationship('KrediSatinAlma', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'ad_soyad': self.ad_soyad,
            'email': self.email,
            'telefon': self.telefon,
            'sektor': self.sektor,
            'kredi': self.kredi,
            'paket_bitis': self.paket_bitis.isoformat() if self.paket_bitis else None,
            'aktif': self.aktif,
            'kayit_tarihi': self.kayit_tarihi.isoformat(),
        }


# ── Sektör numarası tanımı ────────────────────────────────────────────────────
class SektorNumara(db.Model):
    """Her WhatsApp Business numarası bir sektöre aittir."""
    __tablename__ = 'sektor_numaralar'
    id              = db.Column(db.Integer, primary_key=True)
    phone_number_id = db.Column(db.String(50), unique=True, nullable=False)  # Meta phone_number_id
    wa_no           = db.Column(db.String(20), nullable=False)               # +905xxxxxxxxx
    sektor          = db.Column(db.String(50), nullable=False)               # emlak, marangoz
    aciklama        = db.Column(db.String(200))
    access_token    = db.Column(db.Text)                                     # Meta kalıcı token
    aktif           = db.Column(db.Boolean, default=True)
    olusturma       = db.Column(db.DateTime, default=datetime.utcnow)


# ── İşlem kaydı ──────────────────────────────────────────────────────────────
class IslemLog(db.Model):
    __tablename__ = 'islem_log'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    telefon       = db.Column(db.String(20), nullable=False)   # işlemi yapan numara
    sektor        = db.Column(db.String(50))
    islem_tipi    = db.Column(db.String(50))                   # yer_gosterme, teklif, ...
    durum         = db.Column(db.String(20), default='bekliyor') # bekliyor, tamamlandi, hata
    kredi_kullanim = db.Column(db.Float, default=0)
    detay         = db.Column(db.JSON)                         # sektöre özgü veri
    tarih         = db.Column(db.DateTime, default=datetime.utcnow)
    hata_mesaji   = db.Column(db.Text)


# ── Kayıt bekleme listesi ─────────────────────────────────────────────────────
class KayitBekleyen(db.Model):
    """Mesaj geldi ama kayıt yok — kayıt linkini aldı, henüz tamamlamadı."""
    __tablename__ = 'kayit_bekleyen'
    id            = db.Column(db.Integer, primary_key=True)
    telefon       = db.Column(db.String(20), unique=True, nullable=False)
    sektor        = db.Column(db.String(50))
    token         = db.Column(db.String(64), unique=True)      # kayıt linki tokeni
    link_gonderildi = db.Column(db.DateTime, default=datetime.utcnow)
    tamamlandi    = db.Column(db.Boolean, default=False)


# ── Emlakçı Profili ───────────────────────────────────────────────────────────
class EmlakciProfil(db.Model):
    __tablename__ = 'emlakci_profil'
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    # Temel bilgiler
    ad_soyad        = db.Column(db.String(150), nullable=False)
    isletme_adi     = db.Column(db.String(200))
    is_adresi       = db.Column(db.Text)
    telefon         = db.Column(db.String(30))
    eposta          = db.Column(db.String(120))
    # Yasal / Mesleki
    ttyb_no         = db.Column(db.String(100))   # Taşınmaz Ticaret Yetki Belgesi No
    lisans_no       = db.Column(db.String(100))   # Eski/genel lisans no (geriye uyum)
    oda_adi         = db.Column(db.String(200))   # Bağlı oda / borsa adı
    oda_sicil_no    = db.Column(db.String(100))
    ticaret_sicil_no = db.Column(db.String(100))
    vergi_dairesi   = db.Column(db.String(100))
    vergi_no        = db.Column(db.String(50))
    yetki_sehri     = db.Column(db.String(100))
    # Kurumsal / Marka
    slogan          = db.Column(db.Text)
    web_sitesi      = db.Column(db.String(200))
    instagram       = db.Column(db.String(100))
    facebook        = db.Column(db.String(200))
    logo_base64     = db.Column(db.Text)           # Base64 PNG/JPG, max ~150 KB
    # Varsayılan komisyon
    komisyon_kira_ay       = db.Column(db.Integer, default=1)
    komisyon_satis_yuzde   = db.Column(db.Float, default=2.0)
    # Belge gönderim tercihi
    belge_format    = db.Column(db.String(10), default='pdf')  # pdf / resim / ikisi
    guncelleme      = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('emlakci_profil', uselist=False))

    def to_dict(self):
        return {
            'ad_soyad': self.ad_soyad, 'isletme_adi': self.isletme_adi,
            'is_adresi': self.is_adresi, 'telefon': self.telefon, 'eposta': self.eposta,
            'ttyb_no': self.ttyb_no, 'lisans_no': self.lisans_no,
            'oda_adi': self.oda_adi, 'oda_sicil_no': self.oda_sicil_no,
            'ticaret_sicil_no': self.ticaret_sicil_no,
            'vergi_dairesi': self.vergi_dairesi, 'vergi_no': self.vergi_no,
            'yetki_sehri': self.yetki_sehri, 'slogan': self.slogan,
            'web_sitesi': self.web_sitesi, 'instagram': self.instagram,
            'facebook': self.facebook,
            'logo_base64': self.logo_base64,
            'komisyon_kira_ay': self.komisyon_kira_ay,
            'komisyon_satis_yuzde': self.komisyon_satis_yuzde,
            'belge_format': self.belge_format or 'pdf',
        }


# ── Yer Gösterme Kaydı ────────────────────────────────────────────────────────
class YerGosterme(db.Model):
    __tablename__ = 'yer_gosterme'
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    islem_log_id    = db.Column(db.Integer, db.ForeignKey('islem_log.id'), nullable=True)
    # Alıcı
    alici_ad_soyad  = db.Column(db.String(150))
    alici_adres     = db.Column(db.Text)
    alici_tc_no     = db.Column(db.String(20))
    alici_telefon   = db.Column(db.String(30))
    # Taşınmaz
    tasinmaz_sehir  = db.Column(db.String(100))
    tasinmaz_ilce   = db.Column(db.String(100))
    tasinmaz_mahalle = db.Column(db.String(150))
    tasinmaz_ada    = db.Column(db.String(50))
    tasinmaz_parsel = db.Column(db.String(50))
    tasinmaz_adres  = db.Column(db.Text)
    tasinmaz_alan   = db.Column(db.String(50))
    konum_lat       = db.Column(db.Float)
    konum_lng       = db.Column(db.Float)
    # İşlem
    islem_turu      = db.Column(db.String(20))   # kira | satis
    fiyat           = db.Column(db.String(100))
    komisyon_kira_ay       = db.Column(db.Integer)
    komisyon_satis_yuzde   = db.Column(db.Float)
    # Belge
    sablon_no       = db.Column(db.Integer, default=1)
    fotografli_mi   = db.Column(db.Boolean, default=True)
    pdf_token       = db.Column(db.String(64))
    pdf_url         = db.Column(db.String(500))
    sozlesme_tarihi = db.Column(db.Date, default=date.today)
    olusturma       = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='yer_gostermeler')

    def to_dict(self):
        return {
            'id': self.id, 'alici_ad_soyad': self.alici_ad_soyad,
            'alici_telefon': self.alici_telefon, 'alici_tc_no': self.alici_tc_no,
            'tasinmaz_adres': self.tasinmaz_adres, 'tasinmaz_sehir': self.tasinmaz_sehir,
            'tasinmaz_ilce': self.tasinmaz_ilce, 'islem_turu': self.islem_turu,
            'fiyat': self.fiyat, 'sablon_no': self.sablon_no,
            'fotografli_mi': self.fotografli_mi, 'pdf_url': self.pdf_url,
            'olusturma': self.olusturma.isoformat(),
            'sozlesme_tarihi': self.sozlesme_tarihi.isoformat() if self.sozlesme_tarihi else None,
        }


# ── Hızlı Form Token ─────────────────────────────────────────────────────────
class HizliFormToken(db.Model):
    """Web formu için tek kullanımlık token."""
    __tablename__ = 'hizli_form_token'
    id              = db.Column(db.Integer, primary_key=True)
    token           = db.Column(db.String(64), unique=True, nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    telefon         = db.Column(db.String(20), nullable=False)   # WhatsApp numarası
    phone_number_id = db.Column(db.String(50), nullable=False)
    access_token    = db.Column(db.Text, nullable=False)
    kullanildi      = db.Column(db.Boolean, default=False)
    olusturma       = db.Column(db.DateTime, default=datetime.utcnow)


# ── Fatura Bilgisi ────────────────────────────────────────────────────────────
class FaturaBilgisi(db.Model):
    __tablename__ = 'fatura_bilgisi'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    sirket_ad     = db.Column(db.String(200))
    vergi_no      = db.Column(db.String(50))   # TC kimlik veya vergi no
    vergi_dairesi = db.Column(db.String(100))
    il            = db.Column(db.String(50))
    adres         = db.Column(db.Text)
    eposta        = db.Column(db.String(120))
    telefon       = db.Column(db.String(30))
    guncelleme    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'sirket_ad': self.sirket_ad, 'vergi_no': self.vergi_no,
            'vergi_dairesi': self.vergi_dairesi, 'il': self.il,
            'adres': self.adres, 'eposta': self.eposta, 'telefon': self.telefon,
        }


# ── Fatura Kaydı ──────────────────────────────────────────────────────────────
class FaturaKaydi(db.Model):
    __tablename__ = 'fatura_kaydi'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fatura_no     = db.Column(db.String(50), unique=True, nullable=False)
    tarih         = db.Column(db.DateTime, default=datetime.utcnow)
    paket_adi     = db.Column(db.String(100))
    kredi_miktari = db.Column(db.Float)
    tutar_tl      = db.Column(db.Float)
    durum         = db.Column(db.String(20), default='odendi')

    def to_dict(self):
        return {
            'fatura_no': self.fatura_no,
            'tarih': self.tarih.strftime('%d.%m.%Y') if self.tarih else None,
            'paket_adi': self.paket_adi, 'kredi_miktari': self.kredi_miktari,
            'tutar_tl': self.tutar_tl, 'durum': self.durum,
        }


# ── Kredi satın alma ──────────────────────────────────────────────────────────
class KrediSatinAlma(db.Model):
    __tablename__ = 'kredi_satin_alma'
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'))
    paket_adi      = db.Column(db.String(100))
    paket_turu     = db.Column(db.String(20), default='aylik')  # aylik/yillik/ekstra
    gecerlilik_gun = db.Column(db.Integer, default=31)          # 31/365/0
    kredi_miktari  = db.Column(db.Float)
    tutar_tl       = db.Column(db.Float)
    odeme_durumu   = db.Column(db.String(20), default='bekliyor')
    iyzico_token   = db.Column(db.String(200))
    tarih          = db.Column(db.DateTime, default=datetime.utcnow)
