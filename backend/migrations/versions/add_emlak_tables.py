"""add emlak tables

Revision ID: a1b2c3d4e5f6
Revises: 98da1ca4ca81
Create Date: 2026-04-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '98da1ca4ca81'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('hizli_form_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=64), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('telefon', sa.String(length=20), nullable=False),
    sa.Column('phone_number_id', sa.String(length=50), nullable=False),
    sa.Column('access_token', sa.Text(), nullable=False),
    sa.Column('kullanildi', sa.Boolean(), nullable=True),
    sa.Column('olusturma', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )

    op.create_table('emlakci_profil',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('ad_soyad', sa.String(length=150), nullable=False),
    sa.Column('isletme_adi', sa.String(length=200), nullable=True),
    sa.Column('is_adresi', sa.Text(), nullable=True),
    sa.Column('telefon', sa.String(length=30), nullable=True),
    sa.Column('lisans_no', sa.String(length=100), nullable=True),
    sa.Column('vergi_dairesi', sa.String(length=100), nullable=True),
    sa.Column('vergi_no', sa.String(length=50), nullable=True),
    sa.Column('komisyon_kira_ay', sa.Integer(), nullable=True),
    sa.Column('komisyon_satis_yuzde', sa.Float(), nullable=True),
    sa.Column('yetki_sehri', sa.String(length=100), nullable=True),
    sa.Column('guncelleme', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )

    op.create_table('yer_gosterme',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('islem_log_id', sa.Integer(), nullable=True),
    sa.Column('alici_ad_soyad', sa.String(length=150), nullable=True),
    sa.Column('alici_adres', sa.Text(), nullable=True),
    sa.Column('alici_tc_no', sa.String(length=20), nullable=True),
    sa.Column('alici_telefon', sa.String(length=30), nullable=True),
    sa.Column('tasinmaz_sehir', sa.String(length=100), nullable=True),
    sa.Column('tasinmaz_ilce', sa.String(length=100), nullable=True),
    sa.Column('tasinmaz_mahalle', sa.String(length=150), nullable=True),
    sa.Column('tasinmaz_ada', sa.String(length=50), nullable=True),
    sa.Column('tasinmaz_parsel', sa.String(length=50), nullable=True),
    sa.Column('tasinmaz_adres', sa.Text(), nullable=True),
    sa.Column('tasinmaz_alan', sa.String(length=50), nullable=True),
    sa.Column('konum_lat', sa.Float(), nullable=True),
    sa.Column('konum_lng', sa.Float(), nullable=True),
    sa.Column('islem_turu', sa.String(length=20), nullable=True),
    sa.Column('fiyat', sa.String(length=100), nullable=True),
    sa.Column('komisyon_kira_ay', sa.Integer(), nullable=True),
    sa.Column('komisyon_satis_yuzde', sa.Float(), nullable=True),
    sa.Column('sablon_no', sa.Integer(), nullable=True),
    sa.Column('fotografli_mi', sa.Boolean(), nullable=True),
    sa.Column('pdf_token', sa.String(length=64), nullable=True),
    sa.Column('pdf_url', sa.String(length=500), nullable=True),
    sa.Column('sozlesme_tarihi', sa.Date(), nullable=True),
    sa.Column('olusturma', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['islem_log_id'], ['islem_log.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('yer_gosterme')
    op.drop_table('emlakci_profil')
    op.drop_table('hizli_form_token')
