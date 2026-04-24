import React, { useState } from 'react';
import Layout from './Layout';

const YSL = '#25D366';   // WhatsApp yeşili
const DARK = '#0f172a';
const CARD = '#1e293b';
const KARTI = '#263044';
const YAZI = '#e2e8f0';
const DIM  = '#94a3b8';
const DIM2 = '#64748b';

/* ── Küçük komut etiketi ── */
function Etiket({ children }) {
  return (
    <code style={{
      background: '#0f2a1a',
      color: YSL,
      border: `1px solid #1a4a2a`,
      borderRadius: 6,
      padding: '2px 8px',
      fontSize: 13,
      fontFamily: 'monospace',
      whiteSpace: 'nowrap',
    }}>
      {children}
    </code>
  );
}

/* ── Satır: komut + açıklama ── */
function Satir({ komutlar, aciklama, ikon }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: 12,
      padding: '10px 0',
      borderBottom: '1px solid #1e2d3d',
    }}>
      {ikon && <span style={{ fontSize: 18, minWidth: 24, marginTop: 1 }}>{ikon}</span>}
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 4 }}>
          {(Array.isArray(komutlar) ? komutlar : [komutlar]).map(k => (
            <Etiket key={k}>{k}</Etiket>
          ))}
        </div>
        <div style={{ fontSize: 13, color: DIM, lineHeight: 1.5 }}>{aciklama}</div>
      </div>
    </div>
  );
}

/* ── Bölüm kartı ── */
function Bolum({ baslik, ikon, renk = YSL, children }) {
  const [acik, setAcik] = useState(true);
  return (
    <div style={{ background: CARD, borderRadius: 12, marginBottom: 16, overflow: 'hidden' }}>
      <button
        onClick={() => setAcik(a => !a)}
        style={{
          width: '100%', background: 'none', border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: 10,
          padding: '14px 16px', textAlign: 'left',
        }}
      >
        <span style={{ fontSize: 20 }}>{ikon}</span>
        <span style={{ flex: 1, color: renk, fontWeight: 700, fontSize: 15 }}>{baslik}</span>
        <span style={{ color: DIM2, fontSize: 18 }}>{acik ? '▲' : '▼'}</span>
      </button>
      {acik && (
        <div style={{ padding: '0 16px 4px' }}>{children}</div>
      )}
    </div>
  );
}

/* ── Ana sayfa ── */
export default function Komutlar() {
  return (
    <Layout>
      <div style={{ maxWidth: 680, margin: '0 auto' }}>

        {/* Başlık */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>📋</div>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: YAZI, margin: '0 0 6px' }}>
            WhatsApp Komutları
          </h1>
          <p style={{ fontSize: 13, color: DIM, margin: 0 }}>
            Yer Gösterme Sözleşmesi — Tüm komutlar ve kısayollar
          </p>
        </div>

        {/* Yazım hatası notu */}
        <div style={{
          background: '#0f2a1a', border: `1px solid #1a4a2a`,
          borderRadius: 10, padding: '12px 16px', marginBottom: 20,
          display: 'flex', gap: 10, alignItems: 'flex-start',
        }}>
          <span style={{ fontSize: 18 }}>💡</span>
          <div>
            <div style={{ color: YSL, fontWeight: 700, fontSize: 13, marginBottom: 3 }}>
              Yazım hatası toleransı var
            </div>
            <div style={{ color: DIM, fontSize: 12, lineHeight: 1.6 }}>
              Hızlı yazarken hata yapsan da sistem anlar.
              <span style={{ color: YAZI }}> kapat</span> yerine{' '}
              <span style={{ color: YSL }}>kapt · kaat · kapatt</span> yazsan da çalışır.{' '}
              <span style={{ color: YAZI }}>evet</span> yerine{' '}
              <span style={{ color: YSL }}>evett · evat · tamam.</span> de olur.
            </div>
          </div>
        </div>

        {/* Global komutlar */}
        <Bolum baslik="Her an kullanılabilir" ikon="⚡">
          <Satir
            ikon="🔄"
            komutlar={['kapat', 'dur', 'q', 'iptal', 'sıfırla']}
            aciklama="Oturumu sıfırla, baştan başla"
          />
          <Satir
            ikon="💳"
            komutlar={['bakiye', 'kredi']}
            aciklama="Kalan kredi bakiyesini göster"
          />
          <Satir
            ikon="❓"
            komutlar={['yardım', 'help', '?']}
            aciklama="Hoşgeldin mesajını tekrar göster"
          />
          <Satir
            ikon="🔗"
            komutlar={['link', 'form', 'web']}
            aciklama="Web formu linki gönder (24 saat geçerli)"
          />
          <Satir
            ikon="📊"
            komutlar={['özet', 'neredeyim']}
            aciklama="Şu ana kadar girilen bilgileri göster"
            style={{ borderBottom: 'none' }}
          />
        </Bolum>

        {/* Veri girişi */}
        <Bolum baslik="Veri giriş yöntemleri" ikon="📥">
          <Satir
            ikon="👤"
            komutlar={['Kişi kartı']}
            aciklama="Rehberden kişi paylaş → alıcı adı ve telefonu otomatik alınır"
          />
          <Satir
            ikon="📍"
            komutlar={['Konum']}
            aciklama="Konum paylaş → adres otomatik doldurulur"
          />
          <Satir
            ikon="📸"
            komutlar={['Fotoğraf']}
            aciklama="Taşınmaz fotoğrafı gönder (maksimum 4 adet, onay ekranında da eklenebilir)"
          />
          <Satir
            ikon="💬"
            komutlar={['kiralık 15000', 'satılık 450000']}
            aciklama="İşlem türü ve fiyatı tek seferde yaz"
          />
          <Satir
            ikon="📊"
            komutlar={['komisyon 1 ay', '%2 komisyon']}
            aciklama="Kira komisyonu (ay) veya satış komisyonu (%)"
          />
          <Satir
            ikon="✍️"
            komutlar={['Ali Veli 0532... Kadıköy kiralık 18000 komisyon 1 ay']}
            aciklama="Tek mesajda tüm bilgileri yaz — sistem otomatik ayırır"
          />
        </Bolum>

        {/* Şablon */}
        <Bolum baslik="Şablon seçimi" ikon="🖨">
          <Satir komutlar={['1', 'klasik']} aciklama="Klasik şablon — beyaz, sade" />
          <Satir komutlar={['2', 'modern']} aciklama="Modern şablon — koyu arka plan, yeşil vurgu" />
          <Satir komutlar={['3', 'minimalist']} aciklama="Minimalist şablon — açık gri, temiz tasarım" />
          <div style={{ padding: '8px 0 4px', fontSize: 12, color: DIM2 }}>
            Şablon değiştirme veri girişi ve onay ekranında da çalışır.
          </div>
        </Bolum>

        {/* Ek bilgiler */}
        <Bolum baslik="Ek alan komutları" ikon="🗂">
          <Satir
            komutlar={['ada 15']}
            aciklama="Ada numarasını kaydet (PDF'e eklenir)"
          />
          <Satir
            komutlar={['parsel 3']}
            aciklama="Parsel numarasını kaydet"
          />
          <Satir
            komutlar={['m2 120', 'alan 120']}
            aciklama="Taşınmaz alanını m² olarak kaydet"
          />
          <Satir
            komutlar={['foto sil', 'fotosuz']}
            aciklama="Tüm fotoğrafları temizle"
          />
        </Bolum>

        {/* Onay ekranı */}
        <Bolum baslik="Onay ekranı komutları" ikon="✅">
          {/* Onaylama */}
          <div style={{ color: DIM2, fontSize: 11, fontWeight: 700, letterSpacing: 1, padding: '8px 0 4px', textTransform: 'uppercase' }}>
            Belgeyi oluştur
          </div>
          <Satir
            komutlar={['evet', 'tamam', 'ok', 'gönder', 'oluştur', 'hazır', 'bitti', 'yap']}
            aciklama="Belgeyi oluştur ve WhatsApp'a gönder"
          />

          {/* Alan düzeltme */}
          <div style={{ color: DIM2, fontSize: 11, fontWeight: 700, letterSpacing: 1, padding: '12px 0 4px', textTransform: 'uppercase' }}>
            Düzeltme
          </div>
          <Satir ikon="👤" komutlar={['ad', 'alıcı', 'isim']}   aciklama="Alıcı adını sıfırla, yeniden gir" />
          <Satir ikon="📍" komutlar={['adres', 'konum']}         aciklama="Adresi sıfırla, yeniden gir" />
          <Satir ikon="💰" komutlar={['fiyat', 'bedel']}         aciklama="Fiyatı sıfırla veya direkt sayı yaz (25000 → fiyat güncellenir)" />
          <Satir ikon="🔑" komutlar={['tür', 'işlem']}           aciklama="İşlem türünü sıfırla" />
          <Satir ikon="🔑" komutlar={['kiralık', 'satılık']}     aciklama="İşlem türünü direkt değiştir (sıfırlamadan)" />
          <Satir ikon="🪪" komutlar={['tc', 'kimlik']}           aciklama="TC kimlik numarasını sıfırla" />
          <Satir ikon="📞" komutlar={['telefon', 'tel', 'gsm']}  aciklama="Telefon numarasını sıfırla" />
          <Satir ikon="📊" komutlar={['komisyon', 'kom']}        aciklama="Komisyonu sıfırla, yeniden gir" />
          <Satir ikon="🖨" komutlar={['şablon', '1', '2', '3']}  aciklama="Şablon değiştir" />
          <Satir ikon="❌" komutlar={['hayır', 'h', 'n']}        aciklama="Ne düzelteyim? → seçenekler gösterilir" />
        </Bolum>

        {/* Fiyat formatları */}
        <Bolum baslik="Fiyat yazım örnekleri" ikon="💰">
          <Satir komutlar={['15000']}          aciklama="15.000 TL" />
          <Satir komutlar={['15.000']}         aciklama="15.000 TL (nokta binlik ayraç)" />
          <Satir komutlar={['15 bin']}         aciklama="15.000 TL" />
          <Satir komutlar={['1.5 milyon']}     aciklama="1.500.000 TL" />
          <Satir komutlar={['500k']}           aciklama="500.000 TL (Gemini ile)" />
          <div style={{ padding: '8px 0 4px', fontSize: 12, color: DIM2 }}>
            TL/₺ etiketi olmasa da sistem büyük sayıyı fiyat olarak algılar.
          </div>
        </Bolum>

        {/* Oturum */}
        <div style={{
          background: KARTI, borderRadius: 10, padding: '14px 16px', marginBottom: 24,
          fontSize: 13, color: DIM, lineHeight: 1.7,
        }}>
          <span style={{ color: YAZI, fontWeight: 700 }}>⏰ Oturum süresi:</span>{' '}
          30 dakika mesaj gönderilmezse oturum otomatik sıfırlanır.
          Belge oluşturulduktan sonra oturum temizlenir, yeni belge için tekrar başlayın.
        </div>

        {/* Alt not */}
        <div style={{ textAlign: 'center', fontSize: 12, color: DIM2, paddingBottom: 16 }}>
          Herhangi bir komut yazarken yazım hatası yapsan da sistem anlamaya çalışır.
        </div>

      </div>
    </Layout>
  );
}
