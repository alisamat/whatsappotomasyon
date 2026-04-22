import React from 'react';
import { Link } from 'react-router-dom';
import Layout from './Layout';

const WA = '#25D366';

const kart = (emoji, baslik, aciklama) => (
  <div style={{ background: '#fff', borderRadius: 12, padding: 24,
                boxShadow: '0 2px 8px rgba(0,0,0,0.06)', flex: 1, minWidth: 220 }}>
    <div style={{ fontSize: 32, marginBottom: 12 }}>{emoji}</div>
    <div style={{ fontWeight: 700, fontSize: 15, color: '#1e293b', marginBottom: 8 }}>{baslik}</div>
    <div style={{ fontSize: 13, color: '#64748b', lineHeight: 1.6 }}>{aciklama}</div>
  </div>
);

const sektor = (emoji, ad, aciklama) => (
  <div style={{ background: '#f8fafc', borderRadius: 10, padding: '16px 20px',
                border: '1px solid #e2e8f0', display: 'flex', gap: 14, alignItems: 'flex-start' }}>
    <span style={{ fontSize: 28 }}>{emoji}</span>
    <div>
      <div style={{ fontWeight: 700, color: '#1e293b', marginBottom: 4 }}>{ad}</div>
      <div style={{ fontSize: 13, color: '#64748b' }}>{aciklama}</div>
    </div>
  </div>
);

export default function AnaSayfa() {
  return (
    <Layout>
      {/* HERO */}
      <div style={{ textAlign: 'center', padding: '40px 0 48px' }}>
        <div style={{ display: 'inline-block', background: '#dcfce7', color: '#15803d',
                      borderRadius: 20, padding: '4px 14px', fontSize: 12, fontWeight: 600, marginBottom: 16 }}>
          💬 WhatsApp üzerinden tam otomatik
        </div>
        <h1 style={{ fontSize: 40, fontWeight: 800, color: '#0f172a', margin: '0 0 16px', lineHeight: 1.2 }}>
          Sektörünüze özel<br />
          <span style={{ color: WA }}>WhatsApp Otomasyonu</span>
        </h1>
        <p style={{ fontSize: 16, color: '#64748b', maxWidth: 520, margin: '0 auto 32px', lineHeight: 1.7 }}>
          Fotoğraf, konum ve kişi bilgisi gönderin — sistem otomatik belge üretsin,
          size WhatsApp'tan geri göndersin.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          <Link to="/kayit" style={{ background: WA, color: '#fff', borderRadius: 8,
                                     padding: '12px 28px', fontWeight: 700, fontSize: 15,
                                     textDecoration: 'none' }}>
            Ücretsiz Başla
          </Link>
          <Link to="/giris" style={{ background: '#f1f5f9', color: '#1e293b', borderRadius: 8,
                                      padding: '12px 28px', fontWeight: 600, fontSize: 15,
                                      textDecoration: 'none', border: '1px solid #e2e8f0' }}>
            Giriş Yap
          </Link>
        </div>
      </div>

      {/* NASIL ÇALIŞIR */}
      <h2 style={{ textAlign: 'center', fontSize: 22, fontWeight: 700, color: '#1e293b', marginBottom: 24 }}>
        Nasıl Çalışır?
      </h2>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 48 }}>
        {kart('📱', '1. WhatsApp\'tan Gönderin', 'Fotoğraf, konum veya kişi bilgisini numaramıza WhatsApp ile gönderin.')}
        {kart('⚙️', '2. Sistem İşler', 'Yapay zeka destekli sistemimiz bilgilerinizi anında işler ve belgeyi hazırlar.')}
        {kart('📄', '3. Belge Gelir', 'Saniyeler içinde hazır belgeniz WhatsApp\'a gönderilir. Her işlem kredi kullanır.')}
      </div>

      {/* SEKTÖRLER */}
      <h2 style={{ textAlign: 'center', fontSize: 22, fontWeight: 700, color: '#1e293b', marginBottom: 24 }}>
        Hangi Sektörler?
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16, marginBottom: 48 }}>
        {sektor('🏠', 'Emlak', 'Fotoğraf + konum + alıcı → Yer Gösterme Belgesi PDF')}
        {sektor('🪵', 'Marangoz', 'Ölçü ve malzeme bilgisi → Teklif / iş emri')}
        {sektor('🔧', 'Tesisat', 'Sorun fotoğrafı + adres → Müdahale tutanağı')}
        {sektor('➕', 'Daha Fazlası', 'Sektörünüze özel çözüm için bizimle iletişime geçin.')}
      </div>

      {/* KREDİ */}
      <div style={{ background: '#0f172a', borderRadius: 16, padding: '32px 40px', textAlign: 'center', color: '#fff' }}>
        <div style={{ fontSize: 28, marginBottom: 12 }}>💳 Kredi Sistemi</div>
        <p style={{ color: '#94a3b8', fontSize: 14, marginBottom: 24, maxWidth: 480, margin: '0 auto 24px' }}>
          Kayıt olana <strong style={{ color: WA }}>10 ücretsiz kredi</strong> verilir.
          İhtiyacınıza göre ek kredi satın alabilirsiniz.
          Her sektörün işlem maliyeti farklıdır.
        </p>
        <Link to="/kayit" style={{ background: WA, color: '#fff', borderRadius: 8,
                                   padding: '10px 24px', fontWeight: 700, textDecoration: 'none', fontSize: 14 }}>
          Hemen Başla →
        </Link>
      </div>
    </Layout>
  );
}
