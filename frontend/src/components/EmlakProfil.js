import React, { useState, useEffect, useRef } from 'react';
import Layout from './Layout';
import api from '../api';

const G = '#25D366';

const inputSt = {
  width: '100%', boxSizing: 'border-box',
  background: '#fff', border: '1px solid #d1d5db',
  borderRadius: 8, padding: '11px 14px',
  color: '#0f172a', fontSize: 15, outline: 'none', marginBottom: 12,
  WebkitAppearance: 'none',
};
const labelSt = { display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 4 };

function Alan({ label, name, value, onChange, type = 'text', placeholder = '', required = false }) {
  return (
    <div>
      <label style={labelSt}>{label}{required && <span style={{ color: '#dc2626' }}> *</span>}</label>
      <input type={type} name={name} value={value || ''} onChange={onChange}
             placeholder={placeholder} style={inputSt} required={required} />
    </div>
  );
}

function Baslik({ children }) {
  return (
    <div style={{
      fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1,
      color: G, borderBottom: '1px solid #d1fae5',
      paddingBottom: 6, marginBottom: 14, marginTop: 24,
    }}>{children}</div>
  );
}

export default function EmlakProfil() {
  const [form, setForm] = useState({
    ad_soyad: '', isletme_adi: '', is_adresi: '', telefon: '', eposta: '',
    ttyb_no: '', lisans_no: '', oda_adi: '', oda_sicil_no: '', ticaret_sicil_no: '',
    vergi_dairesi: '', vergi_no: '', yetki_sehri: '',
    slogan: '', web_sitesi: '', instagram: '', facebook: '',
    logo_base64: '',
    komisyon_kira_ay: 1, komisyon_satis_yuzde: 2.0,
    belge_format: 'pdf',
  });
  const [yuk, setYuk] = useState(true);
  const [kay, setKay] = useState(false);
  const [msj, setMsj] = useState(null);
  const logoRef = useRef();

  useEffect(() => {
    api.get('/emlak-profil')
      .then(r => { if (r.data.profil) setForm(f => ({ ...f, ...r.data.profil })); })
      .finally(() => setYuk(false));
  }, []);

  const deg = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const logoSec = e => {
    const dosya = e.target.files[0];
    if (!dosya) return;
    if (dosya.size > 200 * 1024) { alert('Logo 200 KB\'dan küçük olmalı.'); return; }
    const reader = new FileReader();
    reader.onload = ev => setForm(f => ({ ...f, logo_base64: ev.target.result }));
    reader.readAsDataURL(dosya);
  };

  const kaydet = async e => {
    e.preventDefault(); setKay(true); setMsj(null);
    try {
      await api.put('/emlak-profil', form);
      setMsj({ tip: 'basari', metin: '✅ Profil kaydedildi.' });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch { setMsj({ tip: 'hata', metin: '❌ Kayıt başarısız.' }); }
    finally { setKay(false); }
  };

  if (yuk) return <Layout><div style={{ color: '#64748b', padding: 48, textAlign: 'center' }}>Yükleniyor…</div></Layout>;

  return (
    <Layout>
      <div style={{ maxWidth: 600, margin: '0 auto' }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: '#0f172a', marginBottom: 4 }}>🏢 Emlakçı Profili</h1>
        <p style={{ color: '#64748b', fontSize: 13, marginBottom: 20 }}>Yer gösterme sözleşmelerinde otomatik kullanılır.</p>

        {msj && (
          <div style={{ padding: '12px 16px', borderRadius: 10, marginBottom: 16, fontSize: 14,
                        background: msj.tip === 'basari' ? '#f0fdf4' : '#fef2f2',
                        color: msj.tip === 'basari' ? '#15803d' : '#dc2626',
                        border: `1px solid ${msj.tip === 'basari' ? '#bbf7d0' : '#fecaca'}` }}>
            {msj.metin}
          </div>
        )}

        <form onSubmit={kaydet} style={{ background: '#fff', borderRadius: 16, padding: '20px 20px 24px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>

          <Baslik>👤 Temel Bilgiler</Baslik>
          <Alan label="Ad Soyad" name="ad_soyad" value={form.ad_soyad} onChange={deg} required placeholder="Ahmet Yılmaz" />
          <Alan label="İşletme Adı" name="isletme_adi" value={form.isletme_adi} onChange={deg} placeholder="Güven Emlak" />
          <Alan label="İş Adresi" name="is_adresi" value={form.is_adresi} onChange={deg} placeholder="Moda Cad. No:5 Kadıköy, İstanbul" />
          <div className="grid-2">
            <Alan label="Telefon" name="telefon" value={form.telefon} onChange={deg} placeholder="0532 111 2222" />
            <Alan label="E-posta" name="eposta" value={form.eposta} onChange={deg} type="email" placeholder="info@firma.com" />
          </div>

          <Baslik>⚖️ Yasal / Mesleki Bilgiler</Baslik>
          <div style={{ background: '#f0fdf4', borderRadius: 8, padding: '10px 14px', marginBottom: 14, fontSize: 12, color: '#15803d' }}>
            💡 TTYB No (Taşınmaz Ticaret Yetki Belgesi) Türkiye'de tüm emlak acentelerinde zorunludur.
          </div>
          <Alan label="TTYB No" name="ttyb_no" value={form.ttyb_no} onChange={deg} placeholder="TR-001234-2024" />
          <div className="grid-2">
            <Alan label="Bağlı Olduğu Oda" name="oda_adi" value={form.oda_adi} onChange={deg} placeholder="İstanbul Emlak Müş. Odası" />
            <Alan label="Oda Sicil No" name="oda_sicil_no" value={form.oda_sicil_no} onChange={deg} placeholder="İST-001234" />
          </div>
          <div className="grid-2">
            <Alan label="Ticaret Sicil No" name="ticaret_sicil_no" value={form.ticaret_sicil_no} onChange={deg} placeholder="İstanbul / 123456" />
            <Alan label="Yetki Şehri" name="yetki_sehri" value={form.yetki_sehri} onChange={deg} placeholder="İstanbul" />
          </div>
          <div className="grid-2">
            <Alan label="Vergi Dairesi" name="vergi_dairesi" value={form.vergi_dairesi} onChange={deg} placeholder="Kadıköy V.D." />
            <Alan label="Vergi No" name="vergi_no" value={form.vergi_no} onChange={deg} placeholder="1234567890" />
          </div>

          <Baslik>📊 Varsayılan Komisyon</Baslik>
          <div className="grid-2">
            <Alan label="Kiralama (ay)" name="komisyon_kira_ay" type="number" value={form.komisyon_kira_ay} onChange={deg} placeholder="1" />
            <Alan label="Satış (%)" name="komisyon_satis_yuzde" type="number" value={form.komisyon_satis_yuzde} onChange={deg} placeholder="2" />
          </div>

          <Baslik>🎨 Kurumsal / Marka</Baslik>
          <Alan label="Slogan" name="slogan" value={form.slogan} onChange={deg} placeholder="Güvenilir Emlak Danışmanınız" />
          <Alan label="Web Sitesi" name="web_sitesi" value={form.web_sitesi} onChange={deg} placeholder="https://firmam.com" />
          <div className="grid-2">
            <Alan label="Instagram" name="instagram" value={form.instagram} onChange={deg} placeholder="@kullanici_adi" />
            <Alan label="Facebook" name="facebook" value={form.facebook} onChange={deg} placeholder="facebook.com/sayfam" />
          </div>

          {/* Logo */}
          <div style={{ marginBottom: 14 }}>
            <label style={labelSt}>Logo (maks. 200 KB · PNG/JPG)</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              {form.logo_base64 ? (
                <img src={form.logo_base64} alt="logo" style={{ height: 56, borderRadius: 8, border: '1px solid #e2e8f0' }} />
              ) : (
                <div style={{ width: 56, height: 56, borderRadius: 8, border: '1px dashed #d1d5db', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94a3b8', fontSize: 22 }}>🏢</div>
              )}
              <input ref={logoRef} type="file" accept="image/*" onChange={logoSec} style={{ display: 'none' }} />
              <button type="button" onClick={() => logoRef.current.click()} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', color: '#374151', borderRadius: 8, padding: '8px 14px', fontSize: 13, cursor: 'pointer' }}>
                {form.logo_base64 ? 'Değiştir' : 'Logo Yükle'}
              </button>
              {form.logo_base64 && (
                <button type="button" onClick={() => setForm(f => ({ ...f, logo_base64: '' }))} style={{ background: 'none', border: 'none', color: '#dc2626', fontSize: 13, cursor: 'pointer' }}>Sil</button>
              )}
            </div>
          </div>

          <Baslik>📄 Belge Gönderim Tercihi</Baslik>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 20 }}>
            {[['pdf', '📄 PDF'], ['resim', '🖼️ Resim'], ['ikisi', '📄+🖼️ Her İkisi']].map(([val, lbl]) => (
              <label key={val} style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 14, color: form.belge_format === val ? G : '#64748b', fontWeight: form.belge_format === val ? 700 : 400 }}>
                <input type="radio" name="belge_format" value={val}
                       checked={form.belge_format === val} onChange={deg}
                       style={{ accentColor: G }} />
                {lbl}
              </label>
            ))}
          </div>

          <button type="submit" disabled={kay} style={{
            width: '100%', background: G, color: '#fff', border: 'none',
            borderRadius: 10, padding: '14px 0', fontSize: 16, fontWeight: 700,
            cursor: kay ? 'not-allowed' : 'pointer', opacity: kay ? 0.7 : 1,
          }}>
            {kay ? 'Kaydediliyor…' : 'Kaydet'}
          </button>
        </form>
      </div>
    </Layout>
  );
}
