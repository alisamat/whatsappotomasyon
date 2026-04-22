"""
PANEL — Kullanıcı dashboard verileri
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, IslemLog

bp = Blueprint('panel', __name__, url_prefix='/api/panel')


@bp.route('/loglar', methods=['GET'])
@jwt_required()
def loglar():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False}), 404

    kayitlar = (
        IslemLog.query
        .filter_by(user_id=user_id)
        .order_by(IslemLog.tarih.desc())
        .limit(50)
        .all()
    )

    def log_dict(l):
        return {
            'id':               l.id,
            'sektor':           l.sektor,
            'islem_tipi':       l.islem_tipi,
            'durum':            l.durum,
            'kredi_kullanimi':  l.kredi_kullanim,
            'aciklama':         _aciklama(l),
            'basarili':         l.durum == 'tamamlandi',
            'olusturulma_tarihi': l.tarih.isoformat() if l.tarih else None,
        }

    return jsonify({'success': True, 'loglar': [log_dict(l) for l in kayitlar]})


def _aciklama(log):
    etiket = {
        'yer_gosterme': 'Yer Gösterme Belgesi',
        'teklif':       'Teklif / İş Emri',
        'tutanak':      'Müdahale Tutanağı',
    }
    islem = etiket.get(log.islem_tipi, log.islem_tipi or 'İşlem')
    if log.durum == 'hata':
        return f'{islem} — Hata'
    if log.durum == 'tamamlandi':
        return f'{islem} — Tamamlandı'
    return f'{islem} — İşleniyor'
