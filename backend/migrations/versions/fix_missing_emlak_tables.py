"""fix missing emlak tables (IF NOT EXISTS)

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS hizli_form_token (
            id SERIAL PRIMARY KEY,
            token VARCHAR(64) NOT NULL UNIQUE,
            user_id INTEGER NOT NULL REFERENCES users(id),
            telefon VARCHAR(20) NOT NULL,
            phone_number_id VARCHAR(50) NOT NULL,
            access_token TEXT NOT NULL,
            kullanildi BOOLEAN DEFAULT FALSE,
            olusturma TIMESTAMP
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS emlakci_profil (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
            ad_soyad VARCHAR(150) NOT NULL,
            isletme_adi VARCHAR(200),
            is_adresi TEXT,
            telefon VARCHAR(30),
            lisans_no VARCHAR(100),
            vergi_dairesi VARCHAR(100),
            vergi_no VARCHAR(50),
            komisyon_kira_ay INTEGER,
            komisyon_satis_yuzde FLOAT,
            yetki_sehri VARCHAR(100),
            guncelleme TIMESTAMP
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS yer_gosterme (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            islem_log_id INTEGER REFERENCES islem_log(id),
            alici_ad_soyad VARCHAR(150),
            alici_adres TEXT,
            alici_tc_no VARCHAR(20),
            alici_telefon VARCHAR(30),
            tasinmaz_sehir VARCHAR(100),
            tasinmaz_ilce VARCHAR(100),
            tasinmaz_mahalle VARCHAR(150),
            tasinmaz_ada VARCHAR(50),
            tasinmaz_parsel VARCHAR(50),
            tasinmaz_adres TEXT,
            tasinmaz_alan VARCHAR(50),
            konum_lat FLOAT,
            konum_lng FLOAT,
            islem_turu VARCHAR(20),
            fiyat VARCHAR(100),
            komisyon_kira_ay INTEGER,
            komisyon_satis_yuzde FLOAT,
            sablon_no INTEGER,
            fotografli_mi BOOLEAN,
            pdf_token VARCHAR(64),
            pdf_url VARCHAR(500),
            sozlesme_tarihi DATE,
            olusturma TIMESTAMP
        )
    """)


def downgrade():
    pass
