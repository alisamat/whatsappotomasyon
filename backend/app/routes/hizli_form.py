"""
HIZLI FORM — Web üzerinden yer gösterme belgesi oluşturma
GET  /api/hizli-form/<token>        — Form verilerini döndür (profil default'ları)
POST /api/hizli-form/<token>/submit — Formu gönder, PDF üret, WhatsApp'a at
"""
import base64
import logging
from datetime import datetime, timedelta, date
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)
bp = Blueprint('hizli_form', __name__, url_prefix='/api/hizli-form')

_TOKEN_TTL_SAAT = 24


def _token_gecerli(hft) -> bool:
    return (
        hft is not None and
        not hft.kullanildi and
        datetime.utcnow() - hft.olusturma < timedelta(hours=_TOKEN_TTL_SAAT)
    )


@bp.route('/<token>', methods=['GET'])
def form_al(token):
    """Token bilgilerini döndür — profil varsa default'ları da gönder."""
    from app.models import HizliFormToken, EmlakciProfil
    hft = HizliFormToken.query.filter_by(token=token).first()
    if not _token_gecerli(hft):
        return jsonify({'success': False,
                        'hata': 'Geçersiz veya süresi dolmuş bağlantı.'}), 404

    profil = EmlakciProfil.query.filter_by(user_id=hft.user_id).first()
    return jsonify({
        'success': True,
        'profil': profil.to_dict() if profil else {},
    })


@bp.route('/<token>/submit', methods=['POST'])
def form_gonder(token):
    """Formu işle, PDF oluştur, WhatsApp'a gönder."""
    from app.models import (db, HizliFormToken, EmlakciProfil,
                             YerGosterme, IslemLog, User)
    from app.services.sektorler.emlak_pdf import pdf_olustur
    from app.services.belge_store import kaydet
    from app.services import whatsapp_client as wa
    from app.services import kayit_akisi as kayit

    hft = HizliFormToken.query.filter_by(token=token).first()
    if not _token_gecerli(hft):
        return jsonify({'success': False,
                        'hata': 'Geçersiz veya süresi dolmuş bağlantı.'}), 404

    d     = request.get_json() or {}
    user  = User.query.get(hft.user_id)
    profil = EmlakciProfil.query.filter_by(user_id=user.id).first()

    if not profil:
        return jsonify({'success': False, 'hata': 'Emlakçı profili bulunamadı.'}), 400

    # Session formatına dönüştür
    fotograflar = []
    for fb64 in (d.get('fotograflar') or []):
        try:
            fotograflar.append(base64.b64decode(fb64))
        except Exception:
            pass

    session = {
        'adim': 'onay_bekleniyor',
        'sablon_no': d.get('sablon_no', 1),
        'fotograflar': fotograflar,
        'konum': None,
        'alici': {
            'ad_soyad': d.get('alici_ad') or '',
            'tc_no':    d.get('alici_tc'),
            'telefon':  d.get('alici_tel'),
            'adres':    None,
        },
        'tasinmaz': {
            'sehir':    d.get('sehir'),
            'ilce':     d.get('ilce'),
            'mahalle':  d.get('mahalle'),
            'ada':      None,
            'parsel':   None,
            'adres':    d.get('adres') or '',
            'alan_m2':  d.get('alan_m2'),
        },
        'islem_turu':          d.get('islem_turu'),
        'fiyat':               str(d.get('fiyat') or ''),
        'komisyon_kira_ay':    d.get('komisyon_kira_ay'),
        'komisyon_satis_yuzde': d.get('komisyon_satis_yuzde'),
    }

    # Zorunlu alan kontrolü
    if not session['alici']['ad_soyad']:
        return jsonify({'success': False, 'hata': 'Alıcı adı zorunlu.'}), 400
    if not session['tasinmaz']['adres']:
        return jsonify({'success': False, 'hata': 'Adres zorunlu.'}), 400
    if not session['islem_turu']:
        return jsonify({'success': False, 'hata': 'İşlem türü zorunlu.'}), 400
    if not session['fiyat']:
        return jsonify({'success': False, 'hata': 'Fiyat zorunlu.'}), 400

    # Kredi kontrolü
    if not kayit.kredi_dus(user, 5):
        return jsonify({'success': False,
                        'hata': f'Yetersiz kredi. Bakiye: {user.kredi:.0f}'}), 402

    # PDF üret
    try:
        pdf_bytes = pdf_olustur(session, profil)
    except Exception as e:
        logger.error(f'[HizliForm] PDF hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'hata': 'PDF oluşturulamadı.'}), 500

    pdf_token = kaydet(pdf_bytes)
    base_url  = current_app.config.get('BASE_URL', '').rstrip('/')
    pdf_url   = f'{base_url}/api/belge/{pdf_token}'

    # DB kaydı
    try:
        t = session['tasinmaz']
        a = session['alici']
        yg = YerGosterme(
            user_id=user.id,
            alici_ad_soyad=a.get('ad_soyad'),
            alici_tc_no=a.get('tc_no'),
            alici_telefon=a.get('telefon'),
            tasinmaz_sehir=t.get('sehir'),
            tasinmaz_ilce=t.get('ilce'),
            tasinmaz_mahalle=t.get('mahalle'),
            tasinmaz_adres=t.get('adres'),
            tasinmaz_alan=str(t.get('alan_m2') or ''),
            islem_turu=session.get('islem_turu'),
            fiyat=session.get('fiyat'),
            komisyon_kira_ay=session.get('komisyon_kira_ay'),
            komisyon_satis_yuzde=session.get('komisyon_satis_yuzde'),
            sablon_no=session.get('sablon_no', 1),
            fotografli_mi=len(fotograflar) > 0,
            pdf_token=pdf_token,
            pdf_url=pdf_url,
            sozlesme_tarihi=date.today(),
        )
        db.session.add(yg)
        db.session.flush()
        log = IslemLog(
            user_id=user.id,
            telefon=hft.telefon,
            sektor='emlak',
            islem_tipi='yer_gosterme',
            durum='tamamlandi',
            kredi_kullanim=5,
            detay={'yer_gosterme_id': yg.id, 'kanal': 'web_form'},
        )
        db.session.add(log)
        yg.islem_log_id = log.id
        hft.kullanildi  = True
        db.session.commit()
    except Exception as e:
        logger.error(f'[HizliForm] Kayıt hatası: {e}', exc_info=True)

    # WhatsApp'a gönder
    alici_adi = session['alici'].get('ad_soyad', 'Alıcı')
    wa.belge_gonder(
        hft.phone_number_id, hft.access_token, hft.telefon,
        pdf_url,
        f'yer_gosterme_{date.today().strftime("%Y%m%d")}.pdf',
        f'✅ {alici_adi} için Yer Gösterme Sözleşmesi hazır! (Web form)',
    )

    return jsonify({'success': True, 'pdf_url': pdf_url})
