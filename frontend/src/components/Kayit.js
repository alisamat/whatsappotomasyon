import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../App';
import api from '../api';

const SEKTORLER = [
  { value: 'emlak',    label: '🏠 Emlak' },
  { value: 'marangoz', label: '🪵 Marangoz' },
  { value: 'tesisat',  label: '🔧 Tesisat' },
  { value: 'diger',    label: '➕ Diğer' },
];

export default function Kayit() {
  const { token } = useParams();
  const { girisYap } = useAuth();
  const nav = useNavigate();

  const [form, setForm] = useState({
    ad_soyad: '', email: '', telefon: '', sifre: '', sektor: 'emlak',
  });
  const [kvkkOnay, setKvkkOnay] = useState(false);
  const [hata, setHata]    = useState('');
  const [yukleniyor, setY] = useState(false);

  const degistir = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  // Token varsa bilgi mesajı
  useEffect(() => {
    if (token) {
      setHata(''); // temizle
    }
  }, [token]);

  const gonder = async e => {
    e.preventDefault();
    if (!kvkkOnay) { setHata('Devam etmek için KVKK metnini onaylamanız gerekiyor.'); return; }
    setHata(''); setY(true);
    try {
      const payload = { ...form };
      if (token) payload.token = token;
      const r = await api.post('/auth/kayit', payload);
      girisYap(r.data.token, r.data.user);
      nav('/panel');
    } catch (err) {
      setHata(err.response?.data?.message || 'Kayıt başarısız.');
    } finally { setY(false); }
  };

  return (
    <div style={{ minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center',
                  background:'#f8fafc', padding:16 }}>
      <div style={{ background:'#fff', borderRadius:16, padding:'40px 36px', width:'100%',
                    maxWidth:440, boxShadow:'0 4px 24px rgba(0,0,0,0.08)' }}>
        <div style={{ textAlign:'center', marginBottom:24 }}>
          <div style={{ fontSize:32, marginBottom:8 }}>💬</div>
          <h1 style={{ fontSize:22, fontWeight:800, color:'#0f172a', margin:0 }}>Kayıt Ol</h1>
          {token
            ? <p style={{ color:'#15803d', background:'#dcfce7', borderRadius:8, padding:'8px 12px',
                           fontSize:13, margin:'8px 0 0' }}>
                WhatsApp'tan yönlendirildiniz. Bilgileri doldurun, 10 kredi hediye!
              </p>
            : <p style={{ color:'#64748b', fontSize:13, margin:'6px 0 0' }}>
                Kayıt olun, 10 ücretsiz kredi kazanın.
              </p>
          }
        </div>

        {hata && <div style={{ background:'#fef2f2', color:'#dc2626', borderRadius:8,
                               padding:'10px 14px', fontSize:13, marginBottom:16 }}>{hata}</div>}

        <form onSubmit={gonder}>
          {[
            ['ad_soyad', 'Ad Soyad', 'text'],
            ['email',    'E-posta',  'email'],
            ['telefon',  'Telefon (WhatsApp)', 'tel'],
            ['sifre',    'Şifre',    'password'],
          ].map(([name, label, type]) => (
            <div key={name} style={{ marginBottom:14 }}>
              <label style={{ fontSize:13, fontWeight:600, color:'#374151', display:'block', marginBottom:5 }}>{label}</label>
              <input name={name} type={type} value={form[name]} onChange={degistir} required
                placeholder={name === 'telefon' ? '+905xxxxxxxxx' : ''}
                style={{ width:'100%', border:'1px solid #e2e8f0', borderRadius:8, padding:'10px 12px',
                         fontSize:14, boxSizing:'border-box', outline:'none' }} />
            </div>
          ))}

          <div style={{ marginBottom:18 }}>
            <label style={{ fontSize:13, fontWeight:600, color:'#374151', display:'block', marginBottom:5 }}>Sektör</label>
            <select name="sektor" value={form.sektor} onChange={degistir}
              style={{ width:'100%', border:'1px solid #e2e8f0', borderRadius:8, padding:'10px 12px',
                       fontSize:14, background:'#fff', outline:'none' }}>
              {SEKTORLER.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
          </div>

          {/* KVKK Onayı */}
          <div style={{ display:'flex', alignItems:'flex-start', gap:10, marginBottom:18 }}>
            <input type="checkbox" id="kvkk" checked={kvkkOnay}
              onChange={e => setKvkkOnay(e.target.checked)}
              style={{ marginTop:2, accentColor:'#25D366', width:16, height:16, flexShrink:0 }} />
            <label htmlFor="kvkk" style={{ fontSize:13, color:'#374151', lineHeight:1.5, cursor:'pointer' }}>
              <Link to="/gizlilik" target="_blank"
                style={{ color:'#25D366', fontWeight:600, textDecoration:'none' }}>
                KVKK Aydınlatma Metni
              </Link>'ni okudum, kişisel verilerimin işlenmesine onay veriyorum.
            </label>
          </div>

          <button type="submit" disabled={yukleniyor || !kvkkOnay}
            style={{ width:'100%', background: kvkkOnay ? '#25D366' : '#94a3b8',
                     color:'#fff', border:'none', borderRadius:8,
                     padding:'12px', fontSize:15, fontWeight:700,
                     cursor: kvkkOnay ? 'pointer' : 'not-allowed' }}>
            {yukleniyor ? 'Kaydediliyor...' : 'Kayıt Ol'}
          </button>
        </form>

        <p style={{ textAlign:'center', fontSize:13, color:'#64748b', marginTop:20 }}>
          Hesabınız var mı? <Link to="/giris" style={{ color:'#25D366', fontWeight:600, textDecoration:'none' }}>Giriş Yap</Link>
        </p>
      </div>
    </div>
  );
}
