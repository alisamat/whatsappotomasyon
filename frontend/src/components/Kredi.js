import React, { useState } from 'react';
import Layout from './Layout';
import { useAuth } from '../App';
import api from '../api';

const WA = '#25D366';

const PAKETLER = [
  { kredi: 10,  fiyat: 29,  popular: false, etiket: 'Başlangıç' },
  { kredi: 25,  fiyat: 59,  popular: true,  etiket: 'En Popüler' },
  { kredi: 60,  fiyat: 119, popular: false, etiket: 'Ekonomik' },
  { kredi: 150, fiyat: 249, popular: false, etiket: 'Pro' },
];

export default function Kredi() {
  const { user, setUser } = useAuth();
  const [yukleniyor, setY] = useState(false);
  const [basarili, setBasarili] = useState('');
  const [hata, setHata] = useState('');

  const satin_al = async (paket) => {
    setY(true); setHata(''); setBasarili('');
    try {
      const r = await api.post('/kredi/satin-al', { kredi: paket.kredi, fiyat: paket.fiyat });
      if (r.data.odeme_url) {
        window.location.href = r.data.odeme_url;
      } else {
        setBasarili(`${paket.kredi} kredi başarıyla eklendi!`);
        setUser(prev => ({ ...prev, kredi: (prev?.kredi || 0) + paket.kredi }));
      }
    } catch (err) {
      setHata(err.response?.data?.message || 'Ödeme başlatılamadı.');
    } finally { setY(false); }
  };

  return (
    <Layout>
      <div style={{ maxWidth: 720, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>💳</div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#0f172a', margin: '0 0 8px' }}>Kredi Satın Al</h1>
          <p style={{ color: '#64748b', fontSize: 13, margin: 0 }}>
            Mevcut bakiye: <strong style={{ color: '#1e293b' }}>{(user?.kredi || 0).toFixed(0)} kredi</strong>
          </p>
        </div>

        {basarili && (
          <div style={{ background: '#f0fdf4', border: '1px solid #86efac', color: '#15803d',
                        borderRadius: 8, padding: '12px 16px', fontSize: 13, marginBottom: 20, textAlign: 'center' }}>
            ✅ {basarili}
          </div>
        )}
        {hata && (
          <div style={{ background: '#fef2f2', color: '#dc2626', borderRadius: 8,
                        padding: '12px 16px', fontSize: 13, marginBottom: 20, textAlign: 'center' }}>
            {hata}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16, marginBottom: 32 }}>
          {PAKETLER.map(p => (
            <div key={p.kredi} style={{
              background: '#fff', borderRadius: 14, padding: '24px 16px', textAlign: 'center',
              boxShadow: p.popular ? '0 4px 20px rgba(37,211,102,0.2)' : '0 2px 8px rgba(0,0,0,0.06)',
              border: p.popular ? `2px solid ${WA}` : '2px solid transparent',
              position: 'relative',
            }}>
              {p.popular && (
                <div style={{
                  position: 'absolute', top: -12, left: '50%', transform: 'translateX(-50%)',
                  background: WA, color: '#fff', borderRadius: 20, padding: '3px 12px',
                  fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap',
                }}>
                  ⭐ {p.etiket}
                </div>
              )}
              {!p.popular && (
                <div style={{ fontSize: 11, color: '#94a3b8', fontWeight: 600, marginBottom: 4 }}>{p.etiket}</div>
              )}
              <div style={{ fontSize: 36, fontWeight: 800, color: '#0f172a', margin: '8px 0 2px' }}>{p.kredi}</div>
              <div style={{ fontSize: 12, color: '#64748b', marginBottom: 16 }}>kredi</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#1e293b', marginBottom: 4 }}>
                {p.fiyat} ₺
              </div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 16 }}>
                {(p.fiyat / p.kredi).toFixed(2)} ₺/kredi
              </div>
              <button onClick={() => satin_al(p)} disabled={yukleniyor}
                style={{
                  width: '100%', background: p.popular ? WA : '#0f172a', color: '#fff',
                  border: 'none', borderRadius: 8, padding: '10px', fontSize: 13,
                  fontWeight: 700, cursor: yukleniyor ? 'not-allowed' : 'pointer',
                  opacity: yukleniyor ? 0.7 : 1,
                }}>
                Satın Al
              </button>
            </div>
          ))}
        </div>

        {/* Kredi Kullanımı */}
        <div style={{ background: '#f8fafc', borderRadius: 12, padding: 20, border: '1px solid #e2e8f0' }}>
          <div style={{ fontWeight: 700, color: '#1e293b', fontSize: 14, marginBottom: 12 }}>
            📊 Kredi Kullanımı
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[
              { sektor: '🏠 Emlak', islem: 'Yer Gösterme Belgesi', kredi: 3 },
              { sektor: '🪵 Marangoz', islem: 'Teklif / İş Emri', kredi: 2 },
              { sektor: '🔧 Tesisat', islem: 'Müdahale Tutanağı', kredi: 2 },
            ].map(item => (
              <div key={item.sektor} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '8px 12px', background: '#fff', borderRadius: 8, fontSize: 13,
              }}>
                <span style={{ color: '#374151' }}>{item.sektor} — {item.islem}</span>
                <span style={{ fontWeight: 700, color: '#dc2626' }}>{item.kredi} kredi</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 10, fontSize: 11, color: '#94a3b8' }}>
            * Kayıt olunca 10 kredi ücretsiz verilir. Ödeme iyzico altyapısıyla güvende.
          </div>
        </div>
      </div>
    </Layout>
  );
}
