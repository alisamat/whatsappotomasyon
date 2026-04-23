import React, { useState, useEffect } from 'react';
import Layout from './Layout';
import api from '../api';

const ALAN = ({ label, name, value, onChange, type = 'text', placeholder = '' }) => (
  <div style={{ marginBottom: 16 }}>
    <label style={{ display: 'block', fontSize: 13, color: '#94a3b8', marginBottom: 6 }}>{label}</label>
    <input
      type={type}
      name={name}
      value={value || ''}
      onChange={onChange}
      placeholder={placeholder}
      style={{
        width: '100%', boxSizing: 'border-box',
        background: '#1e293b', border: '1px solid #334155',
        borderRadius: 8, padding: '10px 14px',
        color: '#f1f5f9', fontSize: 14, outline: 'none',
      }}
    />
  </div>
);

export default function EmlakProfil() {
  const [form, setForm]       = useState({
    ad_soyad: '', isletme_adi: '', is_adresi: '', telefon: '',
    lisans_no: '', vergi_dairesi: '', vergi_no: '',
    komisyon_kira_ay: 1, komisyon_satis_yuzde: 2.0, yetki_sehri: '',
  });
  const [yukleniyor, setYuk]  = useState(true);
  const [kaydediliyor, setKay] = useState(false);
  const [mesaj, setMesaj]     = useState(null);

  useEffect(() => {
    api.get('/emlak-profil')
      .then(r => { if (r.data.profil) setForm(f => ({ ...f, ...r.data.profil })); })
      .catch(() => {})
      .finally(() => setYuk(false));
  }, []);

  const degistir = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const kaydet = async e => {
    e.preventDefault();
    setKay(true);
    setMesaj(null);
    try {
      await api.put('/emlak-profil', form);
      setMesaj({ tip: 'basari', metin: '✅ Profil kaydedildi.' });
    } catch {
      setMesaj({ tip: 'hata', metin: '❌ Kayıt başarısız.' });
    } finally {
      setKay(false);
    }
  };

  if (yukleniyor) return (
    <Layout>
      <div style={{ textAlign: 'center', color: '#64748b', padding: 48 }}>Yükleniyor...</div>
    </Layout>
  );

  return (
    <Layout>
      <div style={{ maxWidth: 600, margin: '0 auto' }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f1f5f9', marginBottom: 8 }}>
          🏢 Emlakçı Profili
        </h1>
        <p style={{ color: '#64748b', fontSize: 14, marginBottom: 28 }}>
          Bu bilgiler yer gösterme sözleşmelerinde otomatik kullanılır.
        </p>

        <form onSubmit={kaydet} style={{ background: '#1e293b', borderRadius: 12, padding: 24 }}>
          <h3 style={{ color: '#25D366', fontSize: 14, fontWeight: 700, marginBottom: 16, textTransform: 'uppercase', letterSpacing: 1 }}>
            Kişisel Bilgiler
          </h3>
          <ALAN label="Ad Soyad *" name="ad_soyad" value={form.ad_soyad} onChange={degistir} placeholder="Ahmet Yılmaz" />
          <ALAN label="İşletme Adı" name="isletme_adi" value={form.isletme_adi} onChange={degistir} placeholder="Güven Emlak" />
          <ALAN label="İş Adresi" name="is_adresi" value={form.is_adresi} onChange={degistir} placeholder="Merkez Mah. Atatürk Cad. No:5 / Kadıköy, İstanbul" />
          <ALAN label="Telefon" name="telefon" value={form.telefon} onChange={degistir} placeholder="0532 111 2222" />

          <h3 style={{ color: '#25D366', fontSize: 14, fontWeight: 700, margin: '24px 0 16px', textTransform: 'uppercase', letterSpacing: 1 }}>
            Lisans & Vergi
          </h3>
          <ALAN label="Lisans No" name="lisans_no" value={form.lisans_no} onChange={degistir} placeholder="TR-001-2024" />
          <ALAN label="Yetki Şehri" name="yetki_sehri" value={form.yetki_sehri} onChange={degistir} placeholder="İstanbul" />
          <ALAN label="Vergi Dairesi" name="vergi_dairesi" value={form.vergi_dairesi} onChange={degistir} placeholder="Kadıköy Vergi Dairesi" />
          <ALAN label="Vergi No" name="vergi_no" value={form.vergi_no} onChange={degistir} placeholder="1234567890" />

          <h3 style={{ color: '#25D366', fontSize: 14, fontWeight: 700, margin: '24px 0 16px', textTransform: 'uppercase', letterSpacing: 1 }}>
            Varsayılan Komisyon
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <ALAN label="Kiralama (ay sayısı)" name="komisyon_kira_ay" type="number"
                  value={form.komisyon_kira_ay} onChange={degistir} placeholder="1" />
            <ALAN label="Satış (% oran)" name="komisyon_satis_yuzde" type="number"
                  value={form.komisyon_satis_yuzde} onChange={degistir} placeholder="2" />
          </div>

          {mesaj && (
            <div style={{
              padding: '10px 14px', borderRadius: 8, marginBottom: 16,
              background: mesaj.tip === 'basari' ? '#052e16' : '#2d1515',
              color: mesaj.tip === 'basari' ? '#4ade80' : '#f87171',
              fontSize: 14,
            }}>
              {mesaj.metin}
            </div>
          )}

          <button type="submit" disabled={kaydediliyor} style={{
            width: '100%', background: '#25D366', color: '#fff',
            border: 'none', borderRadius: 8, padding: '12px 0',
            fontSize: 15, fontWeight: 700, cursor: kaydediliyor ? 'not-allowed' : 'pointer',
            opacity: kaydediliyor ? 0.7 : 1,
          }}>
            {kaydediliyor ? 'Kaydediliyor...' : 'Kaydet'}
          </button>
        </form>

        <div style={{ marginTop: 16, background: '#1e293b', borderRadius: 12, padding: 16 }}>
          <p style={{ color: '#64748b', fontSize: 13, margin: 0 }}>
            💡 <strong style={{ color: '#94a3b8' }}>İpucu:</strong> WhatsApp üzerinden belge oluşturabilmek için bu profili doldurmanız zorunludur. Komisyon değerleri, her işlemde değiştirilebilir.
          </p>
        </div>
      </div>
    </Layout>
  );
}
