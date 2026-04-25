import React, { useState } from 'react';
import Layout from './Layout';
import { useAuth } from '../App';
import api from '../api';

const SEKTORLER = [
  { value: 'emlak',    label: '🏠 Emlak' },
  { value: 'marangoz', label: '🪵 Marangoz' },
  { value: 'tesisat',  label: '🔧 Tesisat' },
  { value: 'diger',    label: '➕ Diğer' },
];

export default function Profil() {
  const { user, setUser } = useAuth();

  const [form, setForm] = useState({
    ad_soyad: user?.ad_soyad || '',
    email:    user?.email || '',
    telefon:  user?.telefon || '',
    sektor:   user?.sektor || 'emlak',
  });
  const [sifreForm, setSifreForm] = useState({ mevcut: '', yeni: '', tekrar: '' });

  const [kaydediliyor, setK] = useState(false);
  const [sifreKaydediliyor, setSK] = useState(false);
  const [mesaj, setMesaj]   = useState('');
  const [sifreMesaj, setSifreMesaj] = useState('');
  const [hata, setHata]   = useState('');
  const [sifreHata, setSifreHata] = useState('');

  const degistir = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }));
  const sifreDegistir = e => setSifreForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const kaydet = async e => {
    e.preventDefault();
    setK(true); setHata(''); setMesaj('');
    try {
      const r = await api.put('/auth/profil', form);
      setUser(r.data.user);
      setMesaj('Profil güncellendi.');
    } catch (err) {
      setHata(err.response?.data?.message || 'Güncelleme başarısız.');
    } finally { setK(false); }
  };

  const sifreKaydet = async e => {
    e.preventDefault();
    if (sifreForm.yeni !== sifreForm.tekrar) {
      setSifreHata('Yeni şifreler eşleşmiyor.'); return;
    }
    setSK(true); setSifreHata(''); setSifreMesaj('');
    try {
      await api.put('/auth/sifre-degistir', { mevcut: sifreForm.mevcut, yeni: sifreForm.yeni });
      setSifreMesaj('Şifre güncellendi.');
      setSifreForm({ mevcut: '', yeni: '', tekrar: '' });
    } catch (err) {
      setSifreHata(err.response?.data?.message || 'Şifre değiştirilemedi.');
    } finally { setSK(false); }
  };

  const inputStyle = {
    width: '100%', border: '1px solid #e2e8f0', borderRadius: 8,
    padding: '10px 12px', fontSize: 14, boxSizing: 'border-box', outline: 'none',
  };
  const labelStyle = { fontSize: 13, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 5 };

  return (
    <Layout>
      <div style={{ maxWidth: 520, margin: '0 auto' }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: '#0f172a', marginBottom: 28 }}>Profil</h1>

        {/* Bilgi Kartı */}
        <div style={{ background: '#f0fdf4', borderRadius: 12, padding: '16px 20px', marginBottom: 24,
                      display: 'flex', alignItems: 'center', gap: 14, border: '1px solid #bbf7d0' }}>
          <div style={{ width: 48, height: 48, borderRadius: '50%', background: '#25D366',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 22, color: '#fff', fontWeight: 700, flexShrink: 0 }}>
            {(user?.ad_soyad || '?')[0].toUpperCase()}
          </div>
          <div>
            <div style={{ fontWeight: 700, color: '#1e293b', fontSize: 15 }}>{user?.ad_soyad}</div>
            <div style={{ fontSize: 12, color: '#64748b' }}>{user?.email} · {(user?.kredi || 0).toFixed(0)} kredi</div>
          </div>
        </div>

        {/* Profil Formu */}
        <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.06)', marginBottom: 20 }}>
          <div style={{ fontWeight: 700, color: '#1e293b', fontSize: 15, marginBottom: 16 }}>Bilgilerimi Güncelle</div>

          {mesaj && <div style={{ background: '#f0fdf4', border: '1px solid #86efac', color: '#15803d',
                                  borderRadius: 8, padding: '10px 14px', fontSize: 13, marginBottom: 14 }}>✅ {mesaj}</div>}
          {hata  && <div style={{ background: '#fef2f2', color: '#dc2626', borderRadius: 8,
                                  padding: '10px 14px', fontSize: 13, marginBottom: 14 }}>{hata}</div>}

          <form onSubmit={kaydet}>
            {[
              ['ad_soyad', 'Ad Soyad', 'text'],
              ['email',    'E-posta',  'email'],
              ['telefon',  'Telefon',  'tel'],
            ].map(([name, label, type]) => (
              <div key={name} style={{ marginBottom: 14 }}>
                <label style={labelStyle}>{label}</label>
                <input name={name} type={type} value={form[name]} onChange={degistir}
                  style={inputStyle} />
              </div>
            ))}

            <div style={{ marginBottom: 18 }}>
              <label style={labelStyle}>Sektör</label>
              <select name="sektor" value={form.sektor} onChange={degistir}
                style={{ ...inputStyle, background: '#fff' }}>
                {SEKTORLER.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>

            <button type="submit" disabled={kaydediliyor}
              style={{ background: '#25D366', color: '#fff', border: 'none', borderRadius: 8,
                       padding: '10px 20px', fontSize: 14, fontWeight: 700, cursor: 'pointer' }}>
              {kaydediliyor ? 'Kaydediliyor...' : 'Kaydet'}
            </button>
          </form>
        </div>

        {/* Şifre Değiştir */}
        <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <div style={{ fontWeight: 700, color: '#1e293b', fontSize: 15, marginBottom: 16 }}>Şifre Değiştir</div>

          {sifreMesaj && <div style={{ background: '#f0fdf4', border: '1px solid #86efac', color: '#15803d',
                                       borderRadius: 8, padding: '10px 14px', fontSize: 13, marginBottom: 14 }}>✅ {sifreMesaj}</div>}
          {sifreHata  && <div style={{ background: '#fef2f2', color: '#dc2626', borderRadius: 8,
                                       padding: '10px 14px', fontSize: 13, marginBottom: 14 }}>{sifreHata}</div>}

          <form onSubmit={sifreKaydet}>
            {[
              ['mevcut', 'Mevcut Şifre'],
              ['yeni',   'Yeni Şifre'],
              ['tekrar', 'Yeni Şifre (Tekrar)'],
            ].map(([name, label]) => (
              <div key={name} style={{ marginBottom: 14 }}>
                <label style={labelStyle}>{label}</label>
                <input name={name} type="password" value={sifreForm[name]} onChange={sifreDegistir}
                  required style={inputStyle} />
              </div>
            ))}

            <button type="submit" disabled={sifreKaydediliyor}
              style={{ background: '#475569', color: '#fff', border: 'none', borderRadius: 8,
                       padding: '10px 20px', fontSize: 14, fontWeight: 700, cursor: 'pointer' }}>
              {sifreKaydediliyor ? 'Güncelleniyor...' : 'Şifreyi Güncelle'}
            </button>
          </form>
        </div>
      </div>
    </Layout>
  );
}
