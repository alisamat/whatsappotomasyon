"""
KAYIT AKIŞI — Bilinmeyen numara sisteme mesaj atınca otomatik yönlendirme
"""
import secrets
import logging
from datetime import datetime
from app.models import db, User, KayitBekleyen
from app.services import whatsapp_client as wa

logger = logging.getLogger(__name__)

FRONTEND_URL = 'https://whatsappotomasyon.com'  # .env'den okunacak


def _telefon_formatlari(tel: str) -> list:
    """905xxxxxxxxx için tüm olası formatları döndür."""
    t = tel.strip().replace('+', '').replace(' ', '')
    if t.startswith('0'):
        t = '90' + t[1:]
    # t artık 905xxxxxxxxx formatında
    return [t, '+' + t, '0' + t[2:]]  # 905xxx, +905xxx, 05xxx


def kayitli_mi(telefon: str) -> User | None:
    """Telefon numarasına göre kayıtlı kullanıcı döndür."""
    formatlar = _telefon_formatlari(telefon)
    return User.query.filter(
        User.aktif == True,
        User.telefon.in_(formatlar)
    ).first()


def kayit_linki_gonder(telefon: str, sektor: str,
                       phone_number_id: str, access_token: str,
                       frontend_url: str = FRONTEND_URL) -> None:
    """
    Kayıt olmayan numaraya tek seferlik kayıt linki gönder.
    Daha önce link gönderildiyse tekrar göndermez.
    """
    mevcut = KayitBekleyen.query.filter_by(telefon=telefon, tamamlandi=False).first()
    if mevcut:
        # Link zaten gönderildi — hatırlatma mesajı
        wa.mesaj_gonder(
            phone_number_id, access_token, telefon,
            f'Kayıt linkiniz daha önce gönderildi. '
            f'Tamamlamak için: {frontend_url}/kayit/{mevcut.token}'
        )
        return

    token = secrets.token_urlsafe(32)
    bekleyen = KayitBekleyen(telefon=telefon, sektor=sektor, token=token)
    db.session.add(bekleyen)
    db.session.commit()

    sektor_adi = {'emlak': 'Emlak', 'marangoz': 'Marangoz'}.get(sektor, sektor.capitalize())
    mesaj = (
        f'👋 Merhaba! WhatsApp Otomasyon sistemine hoş geldiniz.\n\n'
        f'📌 Sektör: {sektor_adi}\n\n'
        f'Hizmetlerimizden yararlanmak için aşağıdaki linkten kayıt olun:\n'
        f'🔗 {frontend_url}/kayit/{token}\n\n'
        f'Kayıt sonrası kredi satın alarak işlemlerinizi başlatabilirsiniz.'
    )
    wa.mesaj_gonder(phone_number_id, access_token, telefon, mesaj)
    logger.info(f'[Kayıt] Link gönderildi → {telefon} ({sektor})')


def kredi_yetersiz_bildir(user: User, gerekli: float,
                           phone_number_id: str, access_token: str,
                           frontend_url: str = FRONTEND_URL) -> None:
    """Kredi yetersizse kullanıcıyı bilgilendir."""
    mesaj = (
        f'⚠️ Yetersiz kredi!\n\n'
        f'Bu işlem için {gerekli:.0f} kredi gerekiyor.\n'
        f'Mevcut bakiyeniz: {user.kredi:.0f} kredi\n\n'
        f'Kredi satın almak için:\n'
        f'🔗 {frontend_url}/kredi'
    )
    wa.mesaj_gonder(phone_number_id, access_token, user.telefon, mesaj)


def abonelik_kontrol(user: User, miktar: float = 1) -> str:
    """
    Abonelik ve kredi durumunu kontrol et.
    Döner: 'ok' | 'paket_bitti' | 'kredi_yetersiz'
    """
    if not user.paket_bitis or user.paket_bitis < datetime.utcnow():
        return 'paket_bitti'
    if user.kredi < miktar:
        return 'kredi_yetersiz'
    return 'ok'


def kredi_dus(user: User, miktar: float, aciklama: str = '') -> bool:
    """Kullanıcının kredisinden düş. Yetmiyorsa veya paket bittiyse False döner."""
    if not user.paket_bitis or user.paket_bitis < datetime.utcnow():
        return False
    if user.kredi < miktar:
        return False
    user.kredi -= miktar
    user.son_islem = datetime.utcnow()
    db.session.commit()
    return True
