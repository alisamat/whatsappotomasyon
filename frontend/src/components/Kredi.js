import React, { useState, useEffect, useCallback } from 'react';
import Layout from './Layout';
import { useAuth } from '../App';
import api from '../api';

const WA = '#25D366';

const S = {
  card:  { background: '#1e293b', borderRadius: 12, padding: 20, marginBottom: 16 },
  label: { fontSize: 12, color: '#64748b', marginBottom: 4, display: 'block' },
  input: { width: '100%', boxSizing: 'border-box', background: '#0f172a', border: '1px solid #334155', borderRadius: 8, padding: '10px 12px', color: '#f1f5f9', fontSize: 14, outline: 'none', marginBottom: 12 },
  btn:   { background: WA, color: '#fff', border: 'none', borderRadius: 8, padding: '11px 20px', fontSize: 14, fontWeight: 700, cursor: 'pointer', width: '100%' },
  hata:  { background: '#2d1515', color: '#f87171', borderRadius: 8, padding: '10px 14px', fontSize: 13, marginBottom: 12 },
  basari:{ background: '#052e16', color: '#4ade80', borderRadius: 8, padding: '10px 14px', fontSize: 13, marginBottom: 12 },
};

const SEKMELER = ['📊 Genel Bakış', '🛒 Satın Al', '📝 Fatura Bilgileri', '🧾 Faturalarım'];

// ── Genel Bakış ──────────────────────────────────────────────────────────────
function GenelBakis({ user, durum, onYenile }) {
  const aktif = durum?.aktif;
  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
        {[
          { label: 'Kalan Kredi',       val: (user?.kredi || 0).toFixed(0) + ' kr', renk: aktif ? WA : '#f87171' },
          { label: 'Son Kullanma',      val: durum?.paket_bitis || '—',              renk: '#f1f5f9' },
          { label: 'Kalan Süre',        val: durum?.kalan_gun != null ? `${durum.kalan_gun} gün` : '—', renk: '#f1f5f9' },
          { label: 'Abonelik Durumu',   val: aktif ? 'Aktif ✓' : 'Pasif ✗',        renk: aktif ? WA : '#f87171' },
        ].map(({ label, val, renk }) => (
          <div key={label} style={{ ...S.card, marginBottom: 0 }}>
            <div style={S.label}>{label}</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: renk }}>{val}</div>
          </div>
        ))}
      </div>

      {!aktif && (
        <div style={{ background: '#1e1a08', border: '1px solid #ca8a04', borderRadius: 10, padding: 16, marginBottom: 12 }}>
          <div style={{ color: '#fbbf24', fontWeight: 700, marginBottom: 4 }}>⚠️ Aktif abonelik yok</div>
          <div style={{ color: '#94a3b8', fontSize: 13 }}>
            Yer gösterme belgesi oluşturmak için aylık veya yıllık paket satın alın.
          </div>
        </div>
      )}

      {aktif && (user?.kredi || 0) < 5 && (
        <div style={{ background: '#1c1008', border: '1px solid #ea580c', borderRadius: 10, padding: 16, marginBottom: 12 }}>
          <div style={{ color: '#fb923c', fontWeight: 700, marginBottom: 4 }}>⚡ Kredi azaldı</div>
          <div style={{ color: '#94a3b8', fontSize: 13 }}>
            Kalan krediniz düşük. Ekstra kredi satın alabilirsiniz.
          </div>
        </div>
      )}

      <div style={S.card}>
        <div style={{ fontWeight: 700, color: '#f1f5f9', marginBottom: 10 }}>📊 Kredi Kullanımı</div>
        {[
          { label: '🏠 Emlak — Yer Gösterme Belgesi', kredi: 5 },
        ].map(item => (
          <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #334155', fontSize: 13 }}>
            <span style={{ color: '#94a3b8' }}>{item.label}</span>
            <span style={{ fontWeight: 700, color: '#f87171' }}>{item.kredi} kredi</span>
          </div>
        ))}
        <div style={{ color: '#475569', fontSize: 11, marginTop: 8 }}>
          Paket alımında abonelik süresi mevcut bitiş tarihine eklenir.
        </div>
      </div>
    </div>
  );
}

// ── Satın Al ─────────────────────────────────────────────────────────────────
function SatinAl({ durum, onBasarili }) {
  const aktif = durum?.aktif;
  const [paketler, setPaketler]   = useState([]);
  const [secili, setSecili]       = useState(null);
  const [kart, setKart]           = useState({ kart_sahibi: '', kart_no: '', son_ay: '', son_yil: '', cvv: '' });
  const [yukleniyor, setY]        = useState(false);
  const [hata, setHata]           = useState('');

  useEffect(() => {
    api.get('/kredi/paketler').then(r => setPaketler(r.data.paketler || [])).catch(() => {});
  }, []);

  const abonelikPaketler = paketler.filter(p => p.turu !== 'ekstra');
  const ekstraPaketler   = paketler.filter(p => p.turu === 'ekstra');

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
      background: secili?.id === p.id ? '#0f2820' : '#0f172a',
      border: `2px solid ${secili?.id === p.id ? WA : p.popular ? WA + '44' : '#334155'}`,
      borderRadius: 12, padding: 16, cursor: 'pointer', position: 'relative',
    }}>
      {p.popular && <div style={{ position: 'absolute', top: -10, right: 12, background: WA, color: '#fff', fontSize: 10, fontWeight: 700, borderRadius: 20, padding: '2px 8px' }}>⭐ Popüler</div>}
      {p.indirim && <div style={{ position: 'absolute', top: -10, left: 12, background: '#f59e0b', color: '#000', fontSize: 10, fontWeight: 700, borderRadius: 20, padding: '2px 8px' }}>%33 İndirim</div>}
      <div style={{ fontWeight: 700, color: '#f1f5f9', marginBottom: 4 }}>{p.ad}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color: WA }}>{p.kredi} <span style={{ fontSize: 13, fontWeight: 400, color: '#64748b' }}>kredi</span></div>
      <div style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', margin: '4px 0' }}>{p.fiyat_tl} ₺</div>
      <div style={{ fontSize: 11, color: '#64748b' }}>{p.aciklama}</div>
    </div>
  );

  return (
    <div>
      <div style={{ fontWeight: 700, color: '#94a3b8', fontSize: 12, textTransform: 'uppercase', marginBottom: 10 }}>Abonelik Paketleri</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px,1fr))', gap: 10, marginBottom: 20 }}>
        {abonelikPaketler.map(p => <PaketKart key={p.id} p={p} />)}
      </div>

      {aktif && ekstraPaketler.length > 0 && (
        <>
          <div style={{ fontWeight: 700, color: '#94a3b8', fontSize: 12, textTransform: 'uppercase', marginBottom: 10 }}>
            Ekstra Kredi <span style={{ color: '#475569', textTransform: 'none', fontWeight: 400 }}>(abonelik süresi uzamaz)</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px,1fr))', gap: 10, marginBottom: 20 }}>
            {ekstraPaketler.map(p => <PaketKart key={p.id} p={p} />)}
          </div>
        </>
      )}

      {secili && (
        <div style={S.card}>
          <div style={{ fontWeight: 700, color: '#f1f5f9', marginBottom: 14 }}>
            💳 {secili.kredi} kredi / {secili.fiyat_tl} ₺
          </div>
          {hata && <div style={S.hata}>{hata}</div>}
          <form onSubmit={ode}>
            <label style={S.label}>Kart Sahibi</label>
            <input style={S.input} name="kart_sahibi" placeholder="AD SOYAD" required
                   value={kart.kart_sahibi} onChange={e => setKart(p => ({ ...p, kart_sahibi: e.target.value }))} />
            <label style={S.label}>Kart Numarası</label>
            <input style={S.input} name="kart_no" placeholder="0000 0000 0000 0000" maxLength={19} required
                   value={kart.kart_no} onChange={e => setKart(p => ({ ...p, kart_no: e.target.value }))} />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10 }}>
              {[['son_ay', 'Ay', 'MM', 2], ['son_yil', 'Yıl', 'YY', 2], ['cvv', 'CVV', '•••', 4]].map(([n, l, ph, ml]) => (
                <div key={n}>
                  <label style={S.label}>{l}</label>
                  <input style={S.input} name={n} placeholder={ph} maxLength={ml} required
                         type={n === 'cvv' ? 'password' : 'text'}
                         value={kart[n]} onChange={e => setKart(p => ({ ...p, [n]: e.target.value }))} />
                </div>
              ))}
            </div>
            <button type="submit" style={{ ...S.btn, opacity: yukleniyor ? 0.7 : 1 }} disabled={yukleniyor}>
              {yukleniyor ? 'Başlatılıyor...' : `${secili.fiyat_tl} ₺ Öde`}
            </button>
            <div style={{ fontSize: 11, color: '#475569', textAlign: 'center', marginTop: 8 }}>
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
    try {
      await api.put('/kredi/fatura-bilgisi', form);
      setMsj({ tip: 'basari', metin: '✅ Kaydedildi.' });
    } catch { setMsj({ tip: 'hata', metin: '❌ Hata.' }); }
    finally { setKay(false); }
  };

  const deg = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  if (yuk) return <div style={{ color: '#64748b', padding: 20 }}>Yükleniyor...</div>;

  const Alan = ({ label, name, placeholder = '' }) => (
    <div><label style={S.label}>{label}</label>
    <input style={S.input} name={name} value={form[name] || ''} onChange={deg} placeholder={placeholder} /></div>
  );

  return (
    <form onSubmit={kaydet} style={S.card}>
      {msj && <div style={msj.tip === 'basari' ? S.basari : S.hata}>{msj.metin}</div>}
      <Alan label="Şirket / Kişi Adı *" name="sirket_ad" placeholder="Ali Veli veya Güven Emlak Ltd." />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        <Alan label="Vergi No / TC *" name="vergi_no" placeholder="10 veya 11 hane" />
        <Alan label="Vergi Dairesi" name="vergi_dairesi" placeholder="Kadıköy V.D." />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 10 }}>
        <Alan label="İl *" name="il" placeholder="İstanbul" />
        <Alan label="E-posta" name="eposta" placeholder="info@firma.com" />
      </div>
      <Alan label="Adres *" name="adres" placeholder="Mah. Sok. No:1 İlçe / Şehir" />
      <Alan label="Telefon" name="telefon" placeholder="0532 111 2222" />
      <button type="submit" style={{ ...S.btn, opacity: kay ? 0.7 : 1 }} disabled={kay}>
        {kay ? 'Kaydediliyor...' : 'Kaydet'}
      </button>
    </form>
  );
}

// ── Faturalarım ──────────────────────────────────────────────────────────────
function Faturalarim() {
  const [liste, setListe] = useState([]);
  const [yuk, setYuk]     = useState(true);

  useEffect(() => {
    api.get('/kredi/faturalar')
      .then(r => setListe(r.data.faturalar || []))
      .finally(() => setYuk(false));
  }, []);

  if (yuk) return <div style={{ color: '#64748b', padding: 20 }}>Yükleniyor...</div>;
  if (!liste.length) return (
    <div style={{ ...S.card, textAlign: 'center', color: '#475569', padding: 32 }}>
      📭 Henüz fatura yok
    </div>
  );

  return (
    <div style={S.card}>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #334155' }}>
              {['Fatura No', 'Tarih', 'Paket', 'Kredi', 'Tutar', 'Durum'].map(h => (
                <th key={h} style={{ padding: '8px 10px', textAlign: 'left', color: '#64748b', fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {liste.map(f => (
              <tr key={f.fatura_no} style={{ borderBottom: '1px solid #1e293b' }}>
                <td style={{ padding: '10px', color: '#94a3b8', fontFamily: 'monospace', fontSize: 11 }}>{f.fatura_no}</td>
                <td style={{ padding: '10px', color: '#94a3b8' }}>{f.tarih}</td>
                <td style={{ padding: '10px', color: '#f1f5f9' }}>{f.paket_adi}</td>
                <td style={{ padding: '10px', color: WA, fontWeight: 700 }}>{f.kredi_miktari}</td>
                <td style={{ padding: '10px', color: '#f1f5f9' }}>{f.tutar_tl} ₺</td>
                <td style={{ padding: '10px' }}>
                  <span style={{ background: '#052e16', color: '#4ade80', borderRadius: 20, padding: '2px 8px', fontSize: 11, fontWeight: 700 }}>
                    {f.durum}
                  </span>
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
    if (params.get('odeme') === 'basarili') {
      window.history.replaceState({}, '', '/kredi');
      setSekme(0);
      setTimeout(yenile, 1000);
    }
    if (params.get('odeme') === 'basarisiz') {
      window.history.replaceState({}, '', '/kredi');
      setSekme(1);
    }
  }, [yenile]);

  return (
    <Layout>
      <div style={{ maxWidth: 680, margin: '0 auto' }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: '#f1f5f9', marginBottom: 20 }}>
          💳 Kredi Yönetimi
        </h1>

        {/* Sekmeler */}
        <div style={{ display: 'flex', gap: 4, marginBottom: 20, overflowX: 'auto' }}>
          {SEKMELER.map((s, i) => (
            <button key={i} onClick={() => setSekme(i)} style={{
              background: sekme === i ? WA : '#1e293b',
              color: sekme === i ? '#fff' : '#94a3b8',
              border: 'none', borderRadius: 8, padding: '8px 14px',
              fontSize: 13, fontWeight: sekme === i ? 700 : 400, cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}>{s}</button>
          ))}
        </div>

        {sekme === 0 && <GenelBakis user={user} durum={durum} onYenile={yenile} />}
        {sekme === 1 && <SatinAl durum={durum} onBasarili={() => { yenile(); setSekme(0); }} />}
        {sekme === 2 && <FaturaBilgileri />}
        {sekme === 3 && <Faturalarim />}
      </div>
    </Layout>
  );
}
