import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_API_URL || '/api';

const S = {
  wrap:   { minHeight: '100vh', background: '#0f172a', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 },
  card:   { background: '#1e293b', borderRadius: 16, padding: 28, width: '100%', maxWidth: 520 },
  title:  { color: '#f1f5f9', fontWeight: 800, fontSize: 20, marginBottom: 4 },
  sub:    { color: '#64748b', fontSize: 13, marginBottom: 24 },
  sec:    { color: '#25D366', fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12, marginTop: 20 },
  label:  { display: 'block', fontSize: 13, color: '#94a3b8', marginBottom: 5 },
  input:  { width: '100%', boxSizing: 'border-box', background: '#0f172a', border: '1px solid #334155', borderRadius: 8, padding: '10px 14px', color: '#f1f5f9', fontSize: 14, outline: 'none', marginBottom: 14 },
  row:    { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 },
  btn:    { width: '100%', background: '#25D366', color: '#fff', border: 'none', borderRadius: 10, padding: '14px 0', fontSize: 16, fontWeight: 700, cursor: 'pointer', marginTop: 8 },
  err:    { background: '#2d1515', color: '#f87171', borderRadius: 8, padding: '10px 14px', fontSize: 13, marginBottom: 12 },
  ok:     { background: '#052e16', color: '#4ade80', borderRadius: 8, padding: '10px 14px', fontSize: 13, marginBottom: 12 },
};

function Alan({ label, name, value, onChange, type = 'text', placeholder = '', required = false, options = null }) {
  return (
    <div>
      <label style={S.label}>{label}{required && <span style={{ color: '#f87171' }}> *</span>}</label>
      {options ? (
        <select name={name} value={value || ''} onChange={onChange} style={S.input}>
          {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      ) : (
        <input type={type} name={name} value={value || ''} onChange={onChange}
               placeholder={placeholder} style={S.input} required={required} />
      )}
    </div>
  );
}

export default function HizliForm() {
  const { token } = useParams();
  const [durum, setDurum]     = useState('yukleniyor'); // yukleniyor | form | gonderiliyor | basari | hata
  const [hata, setHata]       = useState('');
  const [pdfUrl, setPdfUrl]   = useState('');
  const [profil, setProfil]   = useState({});
  const [fotograflar, setFotograflar] = useState([]); // {file, preview, b64}
  const fileRef = useRef();

  const [form, setForm] = useState({
    alici_ad: '', alici_tc: '', alici_tel: '',
    adres: '', sehir: '', ilce: '',
    islem_turu: 'kira', fiyat: '',
    komisyon_kira_ay: '', komisyon_satis_yuzde: '',
    sablon_no: 1,
  });

  useEffect(() => {
    axios.get(`${API}/hizli-form/${token}`)
      .then(r => {
        const p = r.data.profil || {};
        setProfil(p);
        setForm(f => ({
          ...f,
          komisyon_kira_ay: p.komisyon_kira_ay || 1,
          komisyon_satis_yuzde: p.komisyon_satis_yuzde || 2,
        }));
        setDurum('form');
      })
      .catch(e => {
        setHata(e.response?.data?.hata || 'Geçersiz veya süresi dolmuş bağlantı.');
        setDurum('hata');
      });
  }, [token]);

  const degistir = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const fotoEkle = async e => {
    const dosyalar = Array.from(e.target.files);
    const kalan = 4 - fotograflar.length;
    const secilen = dosyalar.slice(0, kalan);

    const yeniler = await Promise.all(secilen.map(dosya => new Promise(resolve => {
      const reader = new FileReader();
      reader.onload = ev => {
        const b64 = ev.target.result.split(',')[1]; // base64 verisi
        resolve({ name: dosya.name, preview: ev.target.result, b64 });
      };
      reader.readAsDataURL(dosya);
    })));

    setFotograflar(f => [...f, ...yeniler]);
    e.target.value = '';
  };

  const fotoCikar = i => setFotograflar(f => f.filter((_, idx) => idx !== i));

  const gonder = async e => {
    e.preventDefault();
    setDurum('gonderiliyor');
    setHata('');
    try {
      const payload = {
        ...form,
        sablon_no: Number(form.sablon_no),
        fiyat: form.fiyat,
        komisyon_kira_ay: form.komisyon_kira_ay ? Number(form.komisyon_kira_ay) : null,
        komisyon_satis_yuzde: form.komisyon_satis_yuzde ? Number(form.komisyon_satis_yuzde) : null,
        fotograflar: fotograflar.map(f => f.b64),
      };
      const r = await axios.post(`${API}/hizli-form/${token}/submit`, payload);
      setPdfUrl(r.data.pdf_url);
      setDurum('basari');
    } catch (err) {
      setHata(err.response?.data?.hata || 'Bir hata oluştu. Tekrar deneyin.');
      setDurum('form');
    }
  };

  if (durum === 'yukleniyor') return (
    <div style={S.wrap}>
      <div style={{ color: '#64748b', fontSize: 16 }}>Yükleniyor...</div>
    </div>
  );

  if (durum === 'hata') return (
    <div style={S.wrap}>
      <div style={{ ...S.card, textAlign: 'center' }}>
        <div style={{ fontSize: 40, marginBottom: 12 }}>❌</div>
        <div style={{ color: '#f87171', fontSize: 15 }}>{hata}</div>
      </div>
    </div>
  );

  if (durum === 'basari') return (
    <div style={S.wrap}>
      <div style={{ ...S.card, textAlign: 'center' }}>
        <div style={{ fontSize: 48, marginBottom: 12 }}>✅</div>
        <div style={{ color: '#4ade80', fontWeight: 700, fontSize: 18, marginBottom: 8 }}>
          Belge hazır!
        </div>
        <div style={{ color: '#94a3b8', fontSize: 14, marginBottom: 20 }}>
          PDF WhatsApp'ınıza gönderildi.
        </div>
        {pdfUrl && (
          <a href={pdfUrl} target="_blank" rel="noreferrer" style={{
            display: 'inline-block', background: '#25D366', color: '#fff',
            borderRadius: 8, padding: '10px 24px', textDecoration: 'none',
            fontWeight: 700, fontSize: 14,
          }}>
            📄 PDF'i Aç
          </a>
        )}
        <div style={{ color: '#475569', fontSize: 12, marginTop: 20 }}>
          Bu pencereyi kapatabilirsiniz.
        </div>
      </div>
    </div>
  );

  return (
    <div style={S.wrap}>
      <div style={S.card}>
        <div style={S.title}>🏠 Yer Gösterme Formu</div>
        {profil.isletme_adi && (
          <div style={S.sub}>{profil.isletme_adi}</div>
        )}

        {hata && <div style={S.err}>{hata}</div>}

        <form onSubmit={gonder}>
          {/* Alıcı */}
          <div style={S.sec}>👤 Alıcı / Kiracı Adayı</div>
          <Alan label="Ad Soyad" name="alici_ad" value={form.alici_ad}
                onChange={degistir} placeholder="Ali Veli" required />
          <div style={S.row}>
            <Alan label="TC Kimlik No" name="alici_tc" value={form.alici_tc}
                  onChange={degistir} placeholder="Opsiyonel" />
            <Alan label="Telefon" name="alici_tel" value={form.alici_tel}
                  onChange={degistir} placeholder="0532 111 2222" />
          </div>

          {/* Taşınmaz */}
          <div style={S.sec}>📍 Taşınmaz</div>
          <Alan label="Adres" name="adres" value={form.adres}
                onChange={degistir} placeholder="Mah. Sok. No:1 İlçe / Şehir" required />
          <div style={S.row}>
            <Alan label="İlçe" name="ilce" value={form.ilce}
                  onChange={degistir} placeholder="Kadıköy" />
            <Alan label="Şehir" name="sehir" value={form.sehir}
                  onChange={degistir} placeholder="İstanbul" />
          </div>

          {/* İşlem */}
          <div style={S.sec}>💰 İşlem Bilgileri</div>
          <div style={S.row}>
            <Alan label="İşlem Türü" name="islem_turu" value={form.islem_turu}
                  onChange={degistir} required
                  options={[{ value: 'kira', label: 'Kiralama' }, { value: 'satis', label: 'Satış' }]} />
            <Alan label="Bedel (TL)" name="fiyat" type="number" value={form.fiyat}
                  onChange={degistir} placeholder="15000" required />
          </div>
          <div style={S.row}>
            {form.islem_turu === 'kira' ? (
              <Alan label="Komisyon (ay)" name="komisyon_kira_ay" type="number"
                    value={form.komisyon_kira_ay} onChange={degistir} placeholder="1" />
            ) : (
              <Alan label="Komisyon (%)" name="komisyon_satis_yuzde" type="number"
                    value={form.komisyon_satis_yuzde} onChange={degistir} placeholder="2" />
            )}
            <Alan label="Şablon" name="sablon_no" value={form.sablon_no}
                  onChange={degistir}
                  options={[
                    { value: 1, label: '1 — Klasik' },
                    { value: 2, label: '2 — Modern' },
                    { value: 3, label: '3 — Minimalist' },
                  ]} />
          </div>

          {/* Fotoğraflar */}
          <div style={S.sec}>📸 Fotoğraflar (isteğe bağlı, max 4)</div>
          {fotograflar.length > 0 && (
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
              {fotograflar.map((f, i) => (
                <div key={i} style={{ position: 'relative' }}>
                  <img src={f.preview} alt="" style={{
                    width: 72, height: 72, objectFit: 'cover', borderRadius: 8,
                    border: '2px solid #334155',
                  }} />
                  <button type="button" onClick={() => fotoCikar(i)} style={{
                    position: 'absolute', top: -6, right: -6,
                    background: '#ef4444', color: '#fff', border: 'none',
                    borderRadius: '50%', width: 20, height: 20, fontSize: 11,
                    cursor: 'pointer', lineHeight: '20px', padding: 0,
                  }}>×</button>
                </div>
              ))}
            </div>
          )}
          {fotograflar.length < 4 && (
            <>
              <input ref={fileRef} type="file" multiple accept="image/*"
                     onChange={fotoEkle} style={{ display: 'none' }} />
              <button type="button" onClick={() => fileRef.current.click()} style={{
                width: '100%', background: 'transparent', border: '1px dashed #334155',
                color: '#94a3b8', borderRadius: 8, padding: '10px 0', fontSize: 13,
                cursor: 'pointer', marginBottom: 14,
              }}>
                + Fotoğraf Ekle ({fotograflar.length}/4)
              </button>
            </>
          )}

          <button type="submit" disabled={durum === 'gonderiliyor'} style={{
            ...S.btn,
            opacity: durum === 'gonderiliyor' ? 0.7 : 1,
            cursor:  durum === 'gonderiliyor' ? 'not-allowed' : 'pointer',
          }}>
            {durum === 'gonderiliyor' ? '⏳ PDF hazırlanıyor...' : '📄 Belgeyi Oluştur'}
          </button>
        </form>
      </div>
    </div>
  );
}
