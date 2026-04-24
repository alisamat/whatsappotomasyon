"""
Geçici belge depolama — /tmp klasörüne UUID token ile kaydeder.
PDF ve PNG destekler.
"""
import os
import uuid

_TMP = '/tmp/wa_belgeler'
os.makedirs(_TMP, exist_ok=True)

_MIME = {'pdf': 'application/pdf', 'png': 'image/png', 'jpg': 'image/jpeg'}


def kaydet(data: bytes, uzanti: str = 'pdf') -> str:
    token = uuid.uuid4().hex
    path = os.path.join(_TMP, f'{token}.{uzanti}')
    with open(path, 'wb') as f:
        f.write(data)
    return token


def al(token: str) -> tuple:
    """(bytes, uzanti) veya (None, 'pdf') döner."""
    if not token.isalnum():
        return None, 'pdf'
    for uzanti in ('pdf', 'png', 'jpg'):
        path = os.path.join(_TMP, f'{token}.{uzanti}')
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return f.read(), uzanti
    return None, 'pdf'


def mime_turu(uzanti: str) -> str:
    return _MIME.get(uzanti, 'application/octet-stream')
