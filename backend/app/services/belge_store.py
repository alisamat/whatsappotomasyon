"""
Geçici PDF depolama — /tmp klasörüne UUID token ile kaydeder.
Worker restart'a ve multi-worker'a karşı dayanıklı.
"""
import os
import uuid

_TMP = '/tmp/wa_belgeler'
os.makedirs(_TMP, exist_ok=True)


def kaydet(pdf_bytes: bytes) -> str:
    token = uuid.uuid4().hex
    path = os.path.join(_TMP, f'{token}.pdf')
    with open(path, 'wb') as f:
        f.write(pdf_bytes)
    return token


def al(token: str) -> bytes | None:
    # Güvenlik: token sadece hex karakterleri içermeli
    if not token.isalnum():
        return None
    path = os.path.join(_TMP, f'{token}.pdf')
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return f.read()
