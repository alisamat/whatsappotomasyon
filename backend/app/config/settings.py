import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # PostgreSQL (Railway)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///whatsappotomasyon.db'
    ).replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Meta / WhatsApp Business API
    META_APP_ID              = os.environ.get('META_APP_ID', '')
    META_APP_SECRET          = os.environ.get('META_APP_SECRET', '')
    META_WEBHOOK_VERIFY_TOKEN = os.environ.get('META_WEBHOOK_VERIFY_TOKEN', 'whatsapp_otomasyon_verify')
    META_API_VERSION         = 'v19.0'

    # Sektör numaraları  {phone_number_id: sektor_kodu}
    # Örnek: {'123456789': 'emlak', '987654321': 'marangoz'}
    # Bu değerleri DB'den de yönetebilirsiniz.
    SEKTOR_NUMARALAR = {}

    # Ön yüz URL (CORS)
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

    # Gemini OCR
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

    # iyzico ödeme
    IYZICO_API_KEY    = os.environ.get('IYZICO_API_KEY', '')
    IYZICO_SECRET_KEY = os.environ.get('IYZICO_SECRET_KEY', '')
    IYZICO_BASE_URL   = os.environ.get('IYZICO_BASE_URL', 'https://sandbox-api.iyzipay.com')

    # Kredi maliyetleri (sektör bazlı)
    ISLEM_MALIYETLERI = {
        'emlak': 5,      # 5 kredi / belge
        'marangoz': 3,
        'varsayilan': 3,
    }
