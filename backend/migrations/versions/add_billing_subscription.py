"""add billing and subscription fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # User tablosuna paket_bitis ekle
    op.add_column('users', sa.Column('paket_bitis', sa.DateTime(), nullable=True))

    # KrediSatinAlma'ya paket_turu ve gecerlilik_gun ekle
    op.add_column('kredi_satin_alma', sa.Column('paket_turu', sa.String(length=20), nullable=True))
    op.add_column('kredi_satin_alma', sa.Column('gecerlilik_gun', sa.Integer(), nullable=True))

    # FaturaBilgisi tablosu
    op.create_table('fatura_bilgisi',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('sirket_ad', sa.String(length=200), nullable=True),
    sa.Column('vergi_no', sa.String(length=50), nullable=True),
    sa.Column('vergi_dairesi', sa.String(length=100), nullable=True),
    sa.Column('il', sa.String(length=50), nullable=True),
    sa.Column('adres', sa.Text(), nullable=True),
    sa.Column('eposta', sa.String(length=120), nullable=True),
    sa.Column('telefon', sa.String(length=30), nullable=True),
    sa.Column('guncelleme', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )

    # FaturaKaydi tablosu
    op.create_table('fatura_kaydi',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('fatura_no', sa.String(length=50), nullable=False),
    sa.Column('tarih', sa.DateTime(), nullable=True),
    sa.Column('paket_adi', sa.String(length=100), nullable=True),
    sa.Column('kredi_miktari', sa.Float(), nullable=True),
    sa.Column('tutar_tl', sa.Float(), nullable=True),
    sa.Column('durum', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('fatura_no')
    )

    # EmlakciProfil yeni alanları
    for col in [
        ('ttyb_no',          sa.String(length=100)),
        ('oda_adi',          sa.String(length=200)),
        ('oda_sicil_no',     sa.String(length=100)),
        ('ticaret_sicil_no', sa.String(length=100)),
        ('eposta',           sa.String(length=120)),
        ('slogan',           sa.Text()),
        ('web_sitesi',       sa.String(length=200)),
        ('instagram',        sa.String(length=100)),
        ('facebook',         sa.String(length=200)),
        ('logo_base64',      sa.Text()),
        ('belge_format',     sa.String(length=10)),
    ]:
        op.add_column('emlakci_profil', sa.Column(col[0], col[1], nullable=True))


def downgrade():
    op.drop_table('fatura_kaydi')
    op.drop_table('fatura_bilgisi')
    op.drop_column('users', 'paket_bitis')
    op.drop_column('kredi_satin_alma', 'paket_turu')
    op.drop_column('kredi_satin_alma', 'gecerlilik_gun')
    for col in ['ttyb_no', 'oda_adi', 'oda_sicil_no', 'ticaret_sicil_no',
                'eposta', 'slogan', 'web_sitesi', 'instagram', 'facebook',
                'logo_base64', 'belge_format']:
        op.drop_column('emlakci_profil', col)
