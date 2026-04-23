"""
Geçici PDF önbelleği — üretilen PDF'leri UUID token ile saklar.
Sunucu yeniden başlayana kadar geçerli.
"""
import uuid

_CACHE: dict[str, bytes] = {}


def kaydet(pdf_bytes: bytes) -> str:
    token = uuid.uuid4().hex
    _CACHE[token] = pdf_bytes
    return token


def al(token: str) -> bytes | None:
    return _CACHE.get(token)
