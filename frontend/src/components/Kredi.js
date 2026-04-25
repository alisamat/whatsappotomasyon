import React, { useState, useEffect, useCallback } from 'react';
import Layout from './Layout';
import { useAuth } from '../App';
import api from '../api';

const G = '#25D366';

const inputSt = {
  width: '100%', boxSizing: 'border-box',
  background: '#fff', border: '1px solid #d1d5db',
  borderRadius: 8, padding: '11px 14px',
  color: '#0f172a', fontSize: 15, outline: 'none', marginBottom: 12,
};
const labelSt = { display: 'block', fontSize: 12, fontWeight: 600, color: '#6b7280', marginBottom: 4 };
const btnSt   = { background: G, color: '#fff', border: 'none', borderRadius: 8, padding: '12px 0', fontSize: 15, fontWeight: 700, cursor: 'pointer', width: '100%', marginTop: 4 };

const SEKMELER = ['📊 Genel', '🛒 Satın Al', '📝 Fatura', '🧾 Faturalarım'];

// ── Genel Bakış ──────────────────────────────────────────────────────────────
function GenelBakis({ user, durum }) {
  const aktif = durum?.aktif;
  return (
    <div>
      <div className="grid-2" style={{ marginBottom: 16 }}>
        {[
          { label: 'Kalan Kredi',     val: (user?.kredi || 0).toFixed(0) + ' kr', renk: aktif ? '#15803d' : '#dc2626' },
          { label: 'Abonelik',        val: aktif ? 'Aktif ✓' : 'Pasif ✗',        renk: aktif ? '#15803d' : '#dc2626' },
          { label: 'Son Kullanma',    val: durum?.paket_bitis || '—',              renk: '#0f172a' },
          { label: 'Kalan Süre',      val: durum?.kalan_gun != null ? `${durum.kalan_gun} gün` : '—', renk: '#0f172a' },
        ].map(({ label, val, renk }) => (
          <div key={label} style={{ background: '#fff', borderRadius: 12, padding: '14px 16px', boxShadow: '0 2px 6px rgba(0,0,0,0.05)', borderLeft: `3px solid ${renk}` }}>
            <div style={{ fontSize: 11, color: '#6b7280', fontWeight: 600, marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: renk }}>{val}</div>
          </div>
        ))}
      </div>

      {!aktif && (
        <div style={{ background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 10, padding: 16, marginBottom: 12 }}>
          <div style={{ color: '#92400e', fontWeight: 700, marginBottom: 4 }}>⚠️ Aktif abonelik yok</div>
          <div style={{ color: '#78350f', fontSize: 13 }}>Yer gösterme belgesi oluşturmak için paket satın alın.</div>
        </div>
      )}

      {aktif && (user?.kredi || 0) < 5 && (
        <div style={{ background: '#fff7ed', border: '1px solid #fed7aa', borderRadius: 10, padding: 16, marginBottom: 12 }}>
          <div style={{ color: '#c2410c', fontWeight: 700, marginBottom: 4 }}>⚡ Kredi azaldı</div>
          <div style={{ color: '#9a3412', fontSize: 13 }}>Ekstra kredi satın alabilirsiniz.</div>
        </div>
      )}

      <div style={{ background: '#fff', borderRadius: 12, padding: '16px 20px', boxShadow: '0 2px 6px rgba(0,0,0,0.05)' }}>
        <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: 12 }}>📊 Kredi Kullanımı</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f1f5f9', fontSize: 14 }}>
          <span style={{ color: '#475569' }}>🏠 Emlak — Yer Gösterme Belgesi</span>
          <span style={{ fontWeight: 700, color: '#dc2626' }}>5 kredi</span>
        </div>
        <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 8 }}>
          Paket alımında abonelik süresi mevcut bitiş tarihine eklenir.
        </div>
      </div>
    </div>
  );
}

// ── Satın Al ─────────────────────────────────────────────────────────────────
function SatinAl({ durum }) {
  const aktif = durum?.aktif;
  const [paketler, setPaketler] = useState([]);
  const [secili, setSecili]     = useState(null);
  const [kart, setKart]         = useState({ kart_sahibi: '', kart_no: '', son_ay: '', son_yil: '', cvv: '' });
  const [yukleniyor, setY]      = useState(false);
  const [hata, setHata]         = useState('');

  useEffect(() => {
    api.get('/kredi/paketler').then(r => setPaketler(r.data.paketler || [])).catch(() => {});
  }, []);

  const abonelik = paketler.filter(p => p.turu !== 'ekstra');
  const ekstra   = paketler.filter(p => p.turu === 'ekstra');

  const ode = async e => {
    e.preventDefault();
    if (!secili) { setHata('Paket seçin.'); return; }
    setY(true); setHata('');
    try {
      const r = await api.post('/kredi/satin-al', { paket_id: secili.id, ...kart });
      if (r.data.html_content) {
        const win = window.open('', '_blank');
        win.document.write(r.data.html_content);
        win.document.close();
      }
    } catch (err) {
      setHata(err.response?.data?.message || 'Ödeme başlatılamadı.');
    } finally { setY(false); }
  };

  const PaketKart = ({ p }) => (
    <div onClick={() => setSecili(p)} style={{
      background: '#fff',
      border: `2px solid ${secili?.id === p.id ? G : p.popular ? G + '55' : '#e2e8f0'}`,
      borderRadius: 12, padding: 16, cursor: 'pointer', position: 'relative',
      boxShadow: secili?.id === p.id ? `0 0 0 3px ${G}22` : '0 2px 6px rgba(0,0,0,0.05)',
      transition: 'border-color 0.15s',
    }}>
      {p.popular && <div style={{ position: 'absolute', top: -10, right: 12, background: G, color: '#fff', fontSize: 10, fontWeight: 700, borderRadius: 20, padding: '2px 8px' }}>⭐ Popüler</div>}
      {p.indirim && <div style={{ position: 'absolute', top: -10, left: 12, background: '#f59e0b', color: '#fff', fontSize: 10, fontWeight: 700, borderRadius: 20, padding: '2px 8px' }}>%33 İndirim</div>}
      <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>{p.ad}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color: G }}>{p.kredi} <span style={{ fontSize: 13, fontWeight: 400, color: '#64748b' }}>kredi</span></div>
      <div style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', margin: '4px 0' }}>{p.fiyat_tl} ₺</div>
      <div style={{ fontSize: 11, color: '#64748b' }}>{p.aciklama}</div>
    </div>
  );

  return (
    <div>
      <div style={{ fontSize: 11, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', marginBottom: 10 }}>Abonelik Paketleri</div>
      <div className="grid-auto" style={{ marginBottom: 20 }}>
        {abonelik.map(p => <PaketKart key={p.id} p={p} />)}
      </div>

      {aktif && ekstra.length > 0 && (<>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', marginBottom: 10 }}>
          Ekstra Kredi <span style={{ textTransform: 'none', fontWeight: 400 }}>(süre uzamaz)</span>
        </div>
        <div className="grid-auto" style={{ marginBottom: 20 }}>
          {ekstra.map(p => <PaketKart key={p.id} p={p} />)}
        </div>
      </>)}

      {secili && (
        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.07)' }}>
          <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: 14, fontSize: 15 }}>
            💳 {secili.kredi} kredi / {secili.fiyat_tl} ₺
          </div>
          {hata && <div style={{ background: '#fef2f2', color: '#dc2626', borderRadius: 8, padding: '10px 14px', fontSize: 13, marginBottom: 12 }}>{hata}</div>}
          <form onSubmit={ode}>
            <label style={labelSt}>Kart Sahibi</label>
            <input style={inputSt} placeholder="AD SOYAD" required
                   value={kart.kart_sahibi} onChange={e => setKart(p => ({ ...p, kart_sahibi: e.target.value }))} />
            <label style={labelSt}>Kart Numarası</label>
            <input style={inputSt} placeholder="0000 0000 0000 0000" maxLength={19} required
                   value={kart.kart_no} onChange={e => setKart(p => ({ ...p, kart_no: e.target.value }))} />
            <div className="grid-3">
              {[['son_ay','Ay','MM',2],['son_yil','Yıl','YY',2],['cvv','CVV','•••',4]].map(([n,l,ph,ml]) => (
                <div key={n}>
                  <label style={labelSt}>{l}</label>
                  <input style={inputSt} placeholder={ph} maxLength={ml} required
                         type={n === 'cvv' ? 'password' : 'text'}
                         value={kart[n]} onChange={e => setKart(p => ({ ...p, [n]: e.target.value }))} />
                </div>
              ))}
            </div>
            <button type="submit" style={{ ...btnSt, opacity: yukleniyor ? 0.7 : 1 }} disabled={yukleniyor}>
              {yukleniyor ? 'Başlatılıyor…' : `${secili.fiyat_tl} ₺ Öde`}
            </button>
            <div style={{ fontSize: 11, color: '#94a3b8', textAlign: 'center', marginTop: 8 }}>
              🔒 KuveytTürk · 3D Secure
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

// ── Fatura Bilgileri ─────────────────────────────────────────────────────────
function FaturaBilgileri() {
  const [form, setForm] = useState({ sirket_ad: '', vergi_no: '', vergi_dairesi: '', il: '', adres: '', eposta: '', telefon: '' });
  const [yuk, setYuk]   = useState(true);
  const [kay, setKay]   = useState(false);
  const [msj, setMsj]   = useState(null);

  useEffect(() => {
    api.get('/kredi/fatura-bilgisi')
      .then(r => { if (r.data.fatura_bilgisi) setForm(f => ({ ...f, ...r.data.fatura_bilgisi })); })
      .finally(() => setYuk(false));
  }, []);

  const kaydet = async e => {
    e.preventDefault(); setKay(true); setMsj(null);
    try { await api.put('/kredi/fatura-bilgisi', form); setMsj({ tip: 'ok', t: '✅ Kaydedildi.' }); }
    catch { setMsj({ tip: 'err', t: '❌ Hata.' }); }
    finally { setKay(false); }
  };

  const deg = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  const Alan = ({ label, name, placeholder = '' }) => (
    <div>
      <label style={labelSt}>{label}</label>
      <input style={inputSt} name={name} value={form[name] || ''} onChange={deg} placeholder={placeholder} />
    </div>
  );

  if (yuk) return <div style={{ color: '#64748b', padding: 20 }}>Yükleniyor…</div>;

  return (
    <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 6px rgba(0,0,0,0.05)' }}>
      {msj && <div style={{ padding: '10px 14px', borderRadius: 8, marginBottom: 12, fontSize: 13,
                            background: msj.tip === 'ok' ? '#f0fdf4' : '#fef2f2',
                            color: msj.tip === 'ok' ? '#15803d' : '#dc2626' }}>{msj.t}</div>}
      <form onSubmit={kaydet}>
        <Alan label="Şirket / Kişi Adı" name="sirket_ad" placeholder="Ali Veli veya Güven Emlak Ltd." />
        <div className="grid-2">
          <Alan label="Vergi No / TC" name="vergi_no" placeholder="10 veya 11 hane" />
          <Alan label="Vergi Dairesi" name="vergi_dairesi" placeholder="Kadıköy V.D." />
        </div>
        <div className="grid-2">
          <Alan label="İl" name="il" placeholder="İstanbul" />
          <Alan label="E-posta" name="eposta" placeholder="info@firma.com" />
        </div>
        <Alan label="Adres" name="adres" placeholder="Mah. Sok. No:1 İlçe / Şehir" />
        <Alan label="Telefon" name="telefon" placeholder="0532 111 2222" />
        <button type="submit" style={{ ...btnSt, opacity: kay ? 0.7 : 1 }} disabled={kay}>
          {kay ? 'Kaydediliyor…' : 'Kaydet'}
        </button>
      </form>
    </div>
  );
}

// ── Faturalarım ──────────────────────────────────────────────────────────────
function Faturalarim() {
  const [liste, setListe] = useState([]);
  const [yuk, setYuk]     = useState(true);

  useEffect(() => {
    api.get('/kredi/faturalar').then(r => setListe(r.data.faturalar || [])).finally(() => setYuk(false));
  }, []);

  if (yuk) return <div style={{ color: '#64748b', padding: 20 }}>Yükleniyor…</div>;
  if (!liste.length) return (
    <div style={{ background: '#fff', borderRadius: 12, padding: 32, textAlign: 'center', color: '#94a3b8', boxShadow: '0 2px 6px rgba(0,0,0,0.05)' }}>
      📭 Henüz fatura yok
    </div>
  );

  return (
    <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 2px 6px rgba(0,0,0,0.05)' }}>
      <div className="overflow-x">
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, minWidth: 480 }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #f1f5f9' }}>
              {['Fatura No', 'Tarih', 'Paket', 'Kredi', 'Tutar', 'Durum'].map(h => (
                <th key={h} style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {liste.map(f => (
              <tr key={f.fatura_no} style={{ borderBottom: '1px solid #f8fafc' }}>
                <td style={{ padding: '10px 14px', color: '#94a3b8', fontFamily: 'monospace', fontSize: 11 }}>{f.fatura_no}</td>
                <td style={{ padding: '10px 14px', color: '#64748b' }}>{f.tarih}</td>
                <td style={{ padding: '10px 14px', color: '#0f172a', fontWeight: 500 }}>{f.paket_adi}</td>
                <td style={{ padding: '10px 14px', color: '#15803d', fontWeight: 700 }}>{f.kredi_miktari}</td>
                <td style={{ padding: '10px 14px', color: '#0f172a' }}>{f.tutar_tl} ₺</td>
                <td style={{ padding: '10px 14px' }}>
                  <span style={{ background: '#f0fdf4', color: '#15803d', borderRadius: 20, padding: '2px 8px', fontSize: 11, fontWeight: 700 }}>{f.durum}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── ANA BİLEŞEN ──────────────────────────────────────────────────────────────
export default function Kredi() {
  const { user, setUser } = useAuth();
  const [sekme, setSekme] = useState(0);
  const [durum, setDurum] = useState(null);

  const yenile = useCallback(() => {
    api.get('/kredi/paket-durum').then(r => setDurum(r.data)).catch(() => {});
    api.get('/auth/me').then(r => setUser(r.data.user)).catch(() => {});
  }, [setUser]);

  useEffect(() => {
    yenile();
    const params = new URLSearchParams(window.location.search);
    if (params.get('odeme') === 'basarili') { window.history.replaceState({}, '', '/kredi'); setSekme(0); setTimeout(yenile, 1000); }
    if (params.get('odeme') === 'basarisiz') { window.history.replaceState({}, '', '/kredi'); setSekme(1); }
  }, [yenile]);

  return (
    <Layout>
      <div style={{ maxWidth: 680, margin: '0 auto' }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: '#0f172a', marginBottom: 20 }}>💳 Kredi Yönetimi</h1>

        {/* Sekmeler */}
        <div style={{ display: 'flex', gap: 4, marginBottom: 20, overflowX: 'auto', paddingBottom: 2 }}>
          {SEKMELER.map((s, i) => (
            <button key={i} onClick={() => setSekme(i)} style={{
              background: sekme === i ? G : '#fff',
              color: sekme === i ? '#fff' : '#64748b',
              border: `1px solid ${sekme === i ? G : '#e2e8f0'}`,
              borderRadius: 8, padding: '8px 14px',
              fontSize: 13, fontWeight: sekme === i ? 700 : 500, cursor: 'pointer',
              whiteSpace: 'nowrap', flexShrink: 0,
            }}>{s}</button>
          ))}
        </div>

        {sekme === 0 && <GenelBakis user={user} durum={durum} />}
        {sekme === 1 && <SatinAl durum={durum} />}
        {sekme === 2 && <FaturaBilgileri />}
        {sekme === 3 && <Faturalarim />}
      </div>
    </Layout>
  );
}
