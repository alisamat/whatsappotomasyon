import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../App';
import api from '../api';

export default function Giris() {
  const { girisYap } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const [form, setForm]   = useState({ email: '', sifre: '' });
  const [hata, setHata]   = useState('');
  const [yukleniyor, setY] = useState(false);

  const degistir = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const gonder = async e => {
    e.preventDefault();
    setHata(''); setY(true);
    try {
      const r = await api.post('/auth/giris', form);
      girisYap(r.data.token, r.data.user);
      nav(loc.state?.from?.pathname || '/panel');
    } catch (err) {
      setHata(err.response?.data?.message || 'Giriş başarısız.');
    } finally { setY(false); }
  };

  return (
    <div style={{ minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center',
                  background:'#f8fafc', padding:16 }}>
      <div style={{ background:'#fff', borderRadius:16, padding:'40px 36px', width:'100%',
                    maxWidth:400, boxShadow:'0 4px 24px rgba(0,0,0,0.08)' }}>
        <div style={{ textAlign:'center', marginBottom:28 }}>
          <div style={{ fontSize:32, marginBottom:8 }}>💬</div>
          <h1 style={{ fontSize:22, fontWeight:800, color:'#0f172a', margin:0 }}>Giriş Yap</h1>
          <p style={{ color:'#64748b', fontSize:13, margin:'6px 0 0' }}>WhatsApp Otomasyon hesabınıza girin</p>
        </div>

        {hata && <div style={{ background:'#fef2f2', color:'#dc2626', borderRadius:8,
                               padding:'10px 14px', fontSize:13, marginBottom:16 }}>{hata}</div>}

        <form onSubmit={gonder}>
          {[['email','E-posta','email'],['sifre','Şifre','password']].map(([name,label,type]) => (
            <div key={name} style={{ marginBottom:16 }}>
              <label style={{ fontSize:13, fontWeight:600, color:'#374151', display:'block', marginBottom:6 }}>{label}</label>
              <input name={name} type={type} value={form[name]} onChange={degistir} required
                style={{ width:'100%', border:'1px solid #e2e8f0', borderRadius:8, padding:'10px 12px',
                         fontSize:14, boxSizing:'border-box', outline:'none' }} />
            </div>
          ))}
          <button type="submit" disabled={yukleniyor}
            style={{ width:'100%', background:'#25D366', color:'#fff', border:'none', borderRadius:8,
                     padding:'12px', fontSize:15, fontWeight:700, cursor:'pointer', marginTop:4 }}>
            {yukleniyor ? 'Giriş yapılıyor...' : 'Giriş Yap'}
          </button>
        </form>

        <p style={{ textAlign:'center', fontSize:13, color:'#64748b', marginTop:20 }}>
          Hesabınız yok mu? <Link to="/kayit" style={{ color:'#25D366', fontWeight:600, textDecoration:'none' }}>Kayıt Ol</Link>
        </p>
      </div>
    </div>
  );
}
