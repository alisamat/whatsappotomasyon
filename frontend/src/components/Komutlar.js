import React, { useState } from 'react';
import Layout from './Layout';

const G = '#16a34a';

function Etiket({ children }) {
  return (
    <code style={{
      background: '#f0fdf4', color: G,
      border: '1px solid #bbf7d0',
      borderRadius: 6, padding: '2px 8px',
      fontSize: 13, fontFamily: 'monospace', whiteSpace: 'nowrap',
    }}>
      {children}
    </code>
  );
}

function Satir({ komutlar, aciklama, ikon }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: 12,
      padding: '10px 0', borderBottom: '1px solid #f1f5f9',
    }}>
      {ikon && <span style={{ fontSize: 18, minWidth: 24, marginTop: 1 }}>{ikon}</span>}
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 4 }}>
          {(Array.isArray(komutlar) ? komutlar : [komutlar]).map(k => (
            <Etiket key={k}>{k}</Etiket>
          ))}
        </div>
        <div style={{ fontSize: 13, color: '#64748b', lineHeight: 1.5 }}>{aciklama}</div>
      </div>
    </div>
  );
}

function Bolum({ baslik, ikon, children }) {
  const [acik, setAcik] = useState(true);
  return (
    <div style={{ background: '#fff', borderRadius: 12, marginBottom: 12, overflow: 'hidden', boxShadow: '0 2px 6px rgba(0,0,0,0.05)' }}>
      <button
        onClick={() => setAcik(a => !a)}
        style={{
          width: '100%', background: 'none', border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: 10,
          padding: '14px 16px', textAlign: 'left',
        }}
      >
        <span style={{ fontSize: 20 }}>{ikon}</span>
        <span style={{ flex: 1, color: G, fontWeight: 700, fontSize: 15 }}>{baslik}</span>
        <span style={{ color: '#94a3b8', fontSize: 16 }}>{acik ? '▲' : '▼'}</span>
      </button>
      {acik && <div style={{ padding: '0 16px 8px' }}>{children}</div>}
    </div>
  );
}

export default function Komutlar() {
  return (
    <Layout>
      <div style={{ maxWidth: 680, margin: '0 auto' }}>

        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>📋</div>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: '#0f172a', margin: '0 0 6px' }}>
            WhatsApp Komutları
          </h1>
          <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
            Yer Gösterme Sözleşmesi — Tüm komutlar ve kısayollar
          </p>
        </div>

        {/* Yazım hatası notu */}
        <div style={{
          background: '#f0fdf4', border: '1px solid #bbf7d0',
          borderRadius: 10, padding: '12px 16px', marginBottom: 20,
          display: 'flex', gap: 10, alignItems: 'flex-start',
        }}>
          <span style={{ fontSize: 18 }}>💡</span>
          <div>
            <div style={{ color: G, fontWeight: 700, fontSize: 13, marginBottom: 3 }}>
              Yazım hatası toleransı var
            </div>
            <div style={{ color: '#64748b', fontSize: 12, lineHeight: 1.6 }}>
              Hızlı yazarken hata yapsan da sistem anlar.
              <span style={{ color: '#0f172a' }}> kapat</span> yerine{' '}
              <span style={{ color: G }}>kapt · kaat · kapatt</span> yazsan da çalışır.{' '}
              <span style={{ color: '#0f172a' }}>evet</span> yerine{' '}
              <span style={{ color: G }}>evett · evat · tamam</span> de olur.
            </div>
          </div>
        </div>

        <Bolum baslik="Her an kullanılabilir" ikon="⚡">
          <Satir ikon="🔄" komutlar={['kapat', 'dur', 'yenile', 'başlat', 'sıfırla', 'q']} aciklama="Oturumu sıfırla, baştan başla" />
          <Satir ikon="💳" komutlar={['bakiye', 'kredi']} aciklama="Kalan kredi bakiyesini göster" />
          <Satir ikon="❓" komutlar={['yardım', 'help', '?']} aciklama="Hoşgeldin mesajını tekrar göster" />
          <Satir ikon="🔗" komutlar={['link', 'form', 'web']} aciklama="Web formu linki gönder (24 saat geçerli)" />
          <Satir ikon="📊" komutlar={['özet', 'neredeyim']} aciklama="Şu ana kadar girilen bilgileri göster" />
        </Bolum>

        <Bolum baslik="Veri giriş yöntemleri" ikon="📥">
          <Satir ikon="👤" komutlar={['Kişi kartı']} aciklama="Rehberden kişi paylaş → alıcı adı ve telefonu otomatik alınır" />
          <Satir ikon="📍" komutlar={['Konum']} aciklama="Konum paylaş → adres otomatik doldurulur" />
          <Satir ikon="📸" komutlar={['Fotoğraf']} aciklama="Taşınmaz fotoğrafı gönder (maksimum 4 adet)" />
          <Satir ikon="💬" komutlar={['kiralık 15000', 'satılık 450000']} aciklama="İşlem türü ve fiyatı tek seferde yaz" />
          <Satir ikon="📊" komutlar={['komisyon 1 ay', '%2 komisyon']} aciklama="Kira komisyonu (ay) veya satış komisyonu (%)" />
          <Satir ikon="✍️" komutlar={['Ali Veli 0532... Kadıköy kiralık 18000 komisyon 1 ay']} aciklama="Tek mesajda tüm bilgileri yaz — sistem otomatik ayırır" />
        </Bolum>

        <Bolum baslik="Şablon seçimi" ikon="🖨">
          <Satir komutlar={['1', 'klasik']} aciklama="Klasik şablon — beyaz, sade" />
          <Satir komutlar={['2', 'modern']} aciklama="Modern şablon — koyu arka plan, yeşil vurgu" />
          <Satir komutlar={['3', 'minimalist']} aciklama="Minimalist şablon — açık gri, temiz tasarım" />
          <div style={{ padding: '8px 0 4px', fontSize: 12, color: '#94a3b8' }}>
            Şablon değiştirme veri girişi ve onay ekranında da çalışır.
          </div>
        </Bolum>

        <Bolum baslik="Ek alan komutları" ikon="🗂">
          <Satir komutlar={['ada 15']} aciklama="Ada numarasını kaydet" />
          <Satir komutlar={['parsel 3']} aciklama="Parsel numarasını kaydet" />
          <Satir komutlar={['m2 120', 'alan 120']} aciklama="Taşınmaz alanını m² olarak kaydet" />
          <Satir komutlar={['foto sil', 'fotosuz']} aciklama="Tüm fotoğrafları temizle" />
        </Bolum>

        <Bolum baslik="Onay ekranı komutları" ikon="✅">
          <div style={{ color: '#94a3b8', fontSize: 11, fontWeight: 700, letterSpacing: 1, padding: '8px 0 4px', textTransform: 'uppercase' }}>Belgeyi oluştur</div>
          <Satir komutlar={['evet', 'tamam', 'ok', 'gönder', 'oluştur', 'hazır', 'bitti', 'yap']} aciklama="Belgeyi oluştur ve WhatsApp'a gönder" />
          <div style={{ color: '#94a3b8', fontSize: 11, fontWeight: 700, letterSpacing: 1, padding: '12px 0 4px', textTransform: 'uppercase' }}>Düzeltme</div>
          <Satir ikon="👤" komutlar={['ad', 'alıcı', 'isim']} aciklama="Alıcı adını sıfırla" />
          <Satir ikon="📍" komutlar={['adres', 'konum']} aciklama="Adresi sıfırla" />
          <Satir ikon="💰" komutlar={['fiyat', 'bedel']} aciklama="Fiyatı sıfırla veya direkt sayı yaz" />
          <Satir ikon="🔑" komutlar={['kiralık', 'satılık']} aciklama="İşlem türünü direkt değiştir" />
          <Satir ikon="🪪" komutlar={['tc', 'kimlik']} aciklama="TC kimlik numarasını sıfırla" />
          <Satir ikon="📞" komutlar={['telefon', 'tel', 'gsm']} aciklama="Telefon numarasını sıfırla" />
          <Satir ikon="📊" komutlar={['komisyon', 'kom']} aciklama="Komisyonu sıfırla" />
          <Satir ikon="🖨" komutlar={['şablon', '1', '2', '3']} aciklama="Şablon değiştir" />
          <Satir ikon="❌" komutlar={['hayır', 'h', 'n']} aciklama="Ne düzelteyim? → seçenekler gösterilir" />
        </Bolum>

        <Bolum baslik="Fiyat yazım örnekleri" ikon="💰">
          <Satir komutlar={['15000']} aciklama="15.000 TL" />
          <Satir komutlar={['15.000']} aciklama="15.000 TL (nokta binlik ayraç)" />
          <Satir komutlar={['15 bin']} aciklama="15.000 TL" />
          <Satir komutlar={['1.5 milyon']} aciklama="1.500.000 TL" />
          <Satir komutlar={['500k']} aciklama="500.000 TL (Gemini ile)" />
        </Bolum>

        <div style={{ background: '#fff', borderRadius: 10, padding: '14px 16px', marginBottom: 20, fontSize: 13, color: '#64748b', lineHeight: 1.7, boxShadow: '0 2px 6px rgba(0,0,0,0.05)' }}>
          <span style={{ color: '#0f172a', fontWeight: 700 }}>⏰ Oturum süresi:</span>{' '}
          30 dakika mesaj gönderilmezse oturum otomatik sıfırlanır.
          Belge oluşturulduktan sonra oturum temizlenir.
        </div>

        <div style={{ textAlign: 'center', fontSize: 12, color: '#94a3b8', paddingBottom: 16 }}>
          Herhangi bir komut yazarken yazım hatası yapsan da sistem anlamaya çalışır.
        </div>

      </div>
    </Layout>
  );
}
