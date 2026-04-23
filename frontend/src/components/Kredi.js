import React, { useState, useEffect } from 'react';
import Layout from './Layout';
import { useAuth } from '../App';
import api from '../api';

const WA = '#25D366';

const PAKETLER = [
  { id: 'p10',  kredi: 10,  fiyat_tl: 29,  popular: false, ad: 'Başlangıç' },
  { id: 'p25',  kredi: 25,  fiyat_tl: 59,  popular: true,  ad: 'Standart' },
  { id: 'p60',  kredi: 60,  fiyat_tl: 119, popular: false, ad: 'Ekonomik' },
  { id: 'p150', kredi: 150, fiyat_tl: 249, popular: false, ad: 'Pro' },
];

export default function Kredi() {
  const { user, setUser } = useAuth();
  const [seciliPaket, setSeciliPaket] = useState(null);
  const [kart, setKart]               = useState({ kart_sahibi: '', kart_no: '', son_ay: '', son_yil: '', cvv: '' });
  const [yukleniyor, setY]            = useState(false);
  const [hata, setHata]               = useState('');

  // URL'de ?odeme=basarili varsa krediyi güncelle
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('odeme') === 'basarili') {
      api.get('/auth/me').then(r => setUser(r.data.user)).catch(() => {});
      window.history.replaceState({}, '', '/kredi');
    }
    if (params.get('odeme') === 'basarisiz') {
      setHata(params.get('hata') || 'Ödeme başarısız.');
      window.history.replaceState({}, '', '/kredi');
    }
  }, []);

  const kartDegistir = e => setKart(p => ({ ...p, [e.target.name]: e.target.value }));

  const odeme_baslat = async e => {
    e.preventDefault();
    if (!seciliPaket) { setHata('Lütfen bir paket seçin.'); return; }
    setY(true); setHata('');
    try {
      const r = await api.post('/kredi/satin-al', {
        paket_id: seciliPaket.id,
        ...kart,
      });
      if (r.data.html_content) {
        // 3D Secure HTML'i yeni pencerede aç
        const win = window.open('', '_blank');
        win.document.write(r.data.html_content);
        win.document.close();
      }
    } catch (err) {
      setHata(err.response?.data?.message || 'Ödeme başlatılamadı.');
    } finally { setY(false); }
  };

  const inputStyle = {
    width: '100%', border: '1px solid #e2e8f0', borderRadius: 8,
    padding: '10px 12px', fontSize: 14, boxSizing: 'border-box', outline: 'none',
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

        {hata && (
          <div style={{ background: '#fef2f2', color: '#dc2626', borderRadius: 8,
                        padding: '12px 16px', fontSize: 13, marginBottom: 20, textAlign: 'center' }}>
            {hata}
          </div>
        )}

        {/* Paketler */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(155px, 1fr))', gap: 14, marginBottom: 28 }}>
          {PAKETLER.map(p => (
            <div key={p.id} onClick={() => setSeciliPaket(p)} style={{
              background: '#fff', borderRadius: 14, padding: '20px 14px', textAlign: 'center',
              boxShadow: seciliPaket?.id === p.id ? '0 0 0 3px #25D366' : p.popular ? '0 4px 20px rgba(37,211,102,0.15)' : '0 2px 8px rgba(0,0,0,0.06)',
              border: seciliPaket?.id === p.id ? `2px solid ${WA}` : p.popular ? `2px solid ${WA}` : '2px solid transparent',
              position: 'relative', cursor: 'pointer', transition: 'all 0.15s',
            }}>
              {p.popular && (
                <div style={{
                  position: 'absolute', top: -11, left: '50%', transform: 'translateX(-50%)',
                  background: WA, color: '#fff', borderRadius: 20, padding: '2px 10px',
                  fontSize: 10, fontWeight: 700, whiteSpace: 'nowrap',
                }}>⭐ {p.ad}</div>
              )}
              {!p.popular && <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 600, marginBottom: 2 }}>{p.ad}</div>}
              <div style={{ fontSize: 32, fontWeight: 800, color: '#0f172a', margin: '6px 0 2px' }}>{p.kredi}</div>
              <div style={{ fontSize: 11, color: '#64748b', marginBottom: 12 }}>kredi</div>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#1e293b' }}>{p.fiyat_tl} ₺</div>
              <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2 }}>
                {(p.fiyat_tl / p.kredi).toFixed(2)} ₺/kredi
              </div>
            </div>
          ))}
        </div>

        {/* Kart Formu */}
        {seciliPaket && (
          <div style={{ background: '#fff', borderRadius: 14, padding: 24, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', marginBottom: 20 }}>
            <div style={{ fontWeight: 700, fontSize: 15, color: '#1e293b', marginBottom: 16 }}>
              💳 Kart Bilgileri — {seciliPaket.kredi} kredi / {seciliPaket.fiyat_tl} ₺
            </div>
            <form onSubmit={odeme_baslat}>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Kart Sahibi Adı</label>
                <input name="kart_sahibi" value={kart.kart_sahibi} onChange={kartDegistir} required
                  placeholder="AD SOYAD" style={inputStyle} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Kart Numarası</label>
                <input name="kart_no" value={kart.kart_no} onChange={kartDegistir} required
                  placeholder="0000 0000 0000 0000" maxLength={19} style={inputStyle} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, marginBottom: 20 }}>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Ay</label>
                  <input name="son_ay" value={kart.son_ay} onChange={kartDegistir} required
                    placeholder="MM" maxLength={2} style={inputStyle} />
                </div>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Yıl</label>
                  <input name="son_yil" value={kart.son_yil} onChange={kartDegistir} required
                    placeholder="YY" maxLength={2} style={inputStyle} />
                </div>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>CVV</label>
                  <input name="cvv" value={kart.cvv} onChange={kartDegistir} required
                    placeholder="000" maxLength={4} type="password" style={inputStyle} />
                </div>
              </div>
              <button type="submit" disabled={yukleniyor} style={{
                width: '100%', background: WA, color: '#fff', border: 'none',
                borderRadius: 8, padding: '12px', fontSize: 15, fontWeight: 700,
                cursor: yukleniyor ? 'not-allowed' : 'pointer', opacity: yukleniyor ? 0.7 : 1,
              }}>
                {yukleniyor ? '3D Secure başlatılıyor...' : `${seciliPaket.fiyat_tl} ₺ Öde`}
              </button>
              <div style={{ fontSize: 11, color: '#94a3b8', textAlign: 'center', marginTop: 10 }}>
                🔒 KuveytTürk Sanal POS · 3D Secure güvencesiyle
              </div>
            </form>
          </div>
        )}

        {/* Kredi Kullanımı */}
        <div style={{ background: '#f8fafc', borderRadius: 12, padding: 20, border: '1px solid #e2e8f0' }}>
          <div style={{ fontWeight: 700, color: '#1e293b', fontSize: 14, marginBottom: 12 }}>📊 Kredi Kullanımı</div>
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
            * Kayıt olunca 10 kredi ücretsiz verilir.
          </div>
        </div>
      </div>
    </Layout>
  );
}
