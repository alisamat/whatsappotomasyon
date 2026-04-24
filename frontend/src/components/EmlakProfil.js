import React, { useState, useEffect, useRef } from 'react';
import Layout from './Layout';
import api from '../api';

const S = {
  input: { width: '100%', boxSizing: 'border-box', background: '#0f172a', border: '1px solid #334155', borderRadius: 8, padding: '10px 14px', color: '#f1f5f9', fontSize: 14, outline: 'none', marginBottom: 14 },
  label: { display: 'block', fontSize: 13, color: '#94a3b8', marginBottom: 5 },
  sec:   { color: '#25D366', fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12, marginTop: 22 },
  row2:  { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 },
};

function Alan({ label, name, value, onChange, type = 'text', placeholder = '', required = false }) {
  return (
    <div>
      <label style={S.label}>{label}{required && <span style={{ color: '#f87171' }}> *</span>}</label>
      <input type={type} name={name} value={value || ''} onChange={onChange}
             placeholder={placeholder} style={S.input} required={required} />
    </div>
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
  const [yuk, setYuk]   = useState(true);
  const [kay, setKay]   = useState(false);
  const [msj, setMsj]   = useState(null);
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
    } catch { setMsj({ tip: 'hata', metin: '❌ Kayıt başarısız.' }); }
    finally { setKay(false); }
  };

  if (yuk) return <Layout><div style={{ color: '#64748b', padding: 48, textAlign: 'center' }}>Yükleniyor...</div></Layout>;

  return (
    <Layout>
      <div style={{ maxWidth: 640, margin: '0 auto' }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f1f5f9', marginBottom: 4 }}>🏢 Emlakçı Profili</h1>
        <p style={{ color: '#64748b', fontSize: 13, marginBottom: 24 }}>Yer gösterme sözleşmelerinde otomatik kullanılır.</p>

        <form onSubmit={kaydet} style={{ background: '#1e293b', borderRadius: 12, padding: 24 }}>

          {/* ── Temel Bilgiler ── */}
          <div style={S.sec}>👤 Temel Bilgiler</div>
          <Alan label="Ad Soyad" name="ad_soyad" value={form.ad_soyad} onChange={deg} required placeholder="Ahmet Yılmaz" />
          <Alan label="İşletme Adı" name="isletme_adi" value={form.isletme_adi} onChange={deg} placeholder="Güven Emlak" />
          <Alan label="İş Adresi" name="is_adresi" value={form.is_adresi} onChange={deg} placeholder="Moda Cad. No:5 Kadıköy, İstanbul" />
          <div style={S.row2}>
            <Alan label="Telefon" name="telefon" value={form.telefon} onChange={deg} placeholder="0532 111 2222" />
            <Alan label="E-posta" name="eposta" value={form.eposta} onChange={deg} type="email" placeholder="info@firmaniz.com" />
          </div>

          {/* ── Yasal / Mesleki ── */}
          <div style={S.sec}>⚖️ Yasal / Mesleki Bilgiler</div>
          <div style={{ background: '#0f172a', borderRadius: 8, padding: '10px 14px', marginBottom: 14, fontSize: 12, color: '#64748b' }}>
            💡 TTYB No (Taşınmaz Ticaret Yetki Belgesi), Türkiye'de faaliyet gösteren tüm emlak acentelerinde zorunludur.
          </div>
          <Alan label="TTYB No (Taşınmaz Ticaret Yetki Belgesi)" name="ttyb_no" value={form.ttyb_no} onChange={deg} placeholder="TR-001234-2024" />
          <div style={S.row2}>
            <Alan label="Bağlı Olduğu Oda / Borsa" name="oda_adi" value={form.oda_adi} onChange={deg} placeholder="İstanbul Emlak Müş. Odası" />
            <Alan label="Oda Sicil No" name="oda_sicil_no" value={form.oda_sicil_no} onChange={deg} placeholder="İST-001234" />
          </div>
          <div style={S.row2}>
            <Alan label="Ticaret Sicil No" name="ticaret_sicil_no" value={form.ticaret_sicil_no} onChange={deg} placeholder="İstanbul / 123456" />
            <Alan label="Yetki Şehri" name="yetki_sehri" value={form.yetki_sehri} onChange={deg} placeholder="İstanbul" />
          </div>
          <div style={S.row2}>
            <Alan label="Vergi Dairesi" name="vergi_dairesi" value={form.vergi_dairesi} onChange={deg} placeholder="Kadıköy V.D." />
            <Alan label="Vergi No" name="vergi_no" value={form.vergi_no} onChange={deg} placeholder="1234567890" />
          </div>

          {/* ── Komisyon ── */}
          <div style={S.sec}>📊 Varsayılan Komisyon</div>
          <div style={S.row2}>
            <Alan label="Kiralama (ay sayısı)" name="komisyon_kira_ay" type="number" value={form.komisyon_kira_ay} onChange={deg} placeholder="1" />
            <Alan label="Satış (% oran)" name="komisyon_satis_yuzde" type="number" value={form.komisyon_satis_yuzde} onChange={deg} placeholder="2" />
          </div>

          {/* ── Kurumsal / Marka ── */}
          <div style={S.sec}>🎨 Kurumsal / Marka</div>
          <Alan label="Slogan" name="slogan" value={form.slogan} onChange={deg} placeholder="Güvenilir Emlak Danışmanınız" />
          <Alan label="Web Sitesi" name="web_sitesi" value={form.web_sitesi} onChange={deg} placeholder="https://firmam.com" />
          <div style={S.row2}>
            <Alan label="Instagram" name="instagram" value={form.instagram} onChange={deg} placeholder="@kullanici_adi" />
            <Alan label="Facebook" name="facebook" value={form.facebook} onChange={deg} placeholder="facebook.com/sayfam" />
          </div>

          {/* Logo */}
          <div>
            <label style={S.label}>Logo (maks. 200 KB · PNG/JPG)</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
              {form.logo_base64 ? (
                <img src={form.logo_base64} alt="logo" style={{ height: 56, borderRadius: 8, border: '1px solid #334155' }} />
              ) : (
                <div style={{ width: 56, height: 56, borderRadius: 8, border: '1px dashed #334155', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#475569', fontSize: 22 }}>🏢</div>
              )}
              <input ref={logoRef} type="file" accept="image/*" onChange={logoSec} style={{ display: 'none' }} />
              <button type="button" onClick={() => logoRef.current.click()} style={{ background: '#0f172a', border: '1px solid #334155', color: '#94a3b8', borderRadius: 8, padding: '8px 14px', fontSize: 13, cursor: 'pointer' }}>
                {form.logo_base64 ? 'Değiştir' : 'Logo Yükle'}
              </button>
              {form.logo_base64 && (
                <button type="button" onClick={() => setForm(f => ({ ...f, logo_base64: '' }))} style={{ background: 'none', border: 'none', color: '#f87171', fontSize: 13, cursor: 'pointer' }}>
                  Sil
                </button>
              )}
            </div>
          </div>

          {/* ── Belge Gönderim Tercihi ── */}
          <div style={S.sec}>📄 Belge Gönderim Tercihi</div>
          <div style={{ marginBottom: 14 }}>
            <label style={S.label}>WhatsApp'a hangi formatta gönderilsin?</label>
            <div style={{ display: 'flex', gap: 10 }}>
              {[['pdf', '📄 PDF'], ['resim', '🖼️ Resim'], ['ikisi', '📄+🖼️ Her İkisi']].map(([val, lbl]) => (
                <label key={val} style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 13, color: form.belge_format === val ? '#25D366' : '#94a3b8', fontWeight: form.belge_format === val ? 700 : 400 }}>
                  <input type="radio" name="belge_format" value={val}
                         checked={form.belge_format === val}
                         onChange={deg} style={{ accentColor: '#25D366' }} />
                  {lbl}
                </label>
              ))}
            </div>
          </div>

          {msj && (
            <div style={{ padding: '10px 14px', borderRadius: 8, marginBottom: 14, fontSize: 14, background: msj.tip === 'basari' ? '#052e16' : '#2d1515', color: msj.tip === 'basari' ? '#4ade80' : '#f87171' }}>
              {msj.metin}
            </div>
          )}

          <button type="submit" disabled={kay} style={{ width: '100%', background: '#25D366', color: '#fff', border: 'none', borderRadius: 8, padding: '12px 0', fontSize: 15, fontWeight: 700, cursor: kay ? 'not-allowed' : 'pointer', opacity: kay ? 0.7 : 1 }}>
            {kay ? 'Kaydediliyor...' : 'Kaydet'}
          </button>
        </form>
      </div>
    </Layout>
  );
}
