"""
VERİ MODELLERİ
"""
from datetime import datetime
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


# ── Kredi satın alma ──────────────────────────────────────────────────────────
class KrediSatinAlma(db.Model):
    __tablename__ = 'kredi_satin_alma'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'))
    paket_adi     = db.Column(db.String(100))
    kredi_miktari = db.Column(db.Float)
    tutar_tl      = db.Column(db.Float)
    odeme_durumu  = db.Column(db.String(20), default='bekliyor')  # bekliyor, onaylandi, iptal
    iyzico_token  = db.Column(db.String(200))
    tarih         = db.Column(db.DateTime, default=datetime.utcnow)
