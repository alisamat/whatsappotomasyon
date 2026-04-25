import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_API_URL || '/api';

/* ── Renk paleti (açık tema) ── */
const C = {
  bg:      '#f0fdf4',   // açık yeşilimsi beyaz
  card:    '#ffffff',
  border:  '#d1fae5',
  green:   '#16a34a',
  greenL:  '#dcfce7',
  text:    '#111827',
  sub:     '#6b7280',
  label:   '#374151',
  input:   '#ffffff',
  inputBr: '#d1d5db',
  err:     '#fef2f2',
  errTxt:  '#dc2626',
  ok:      '#f0fdf4',
  okTxt:   '#16a34a',
};

const inputStyle = {
  width: '100%',
  boxSizing: 'border-box',
  background: C.input,
  border: `1px solid ${C.inputBr}`,
  borderRadius: 8,
  padding: '11px 14px',
  color: C.text,
  fontSize: 15,
  outline: 'none',
  marginBottom: 12,
  WebkitAppearance: 'none',
};

function Alan({ label, name, value, onChange, type = 'text', placeholder = '', required = false, options = null }) {
  return (
    <div>
      <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: C.label, marginBottom: 4 }}>
        {label}{required && <span style={{ color: C.errTxt }}> *</span>}
      </label>
      {options ? (
        <select name={name} value={value || ''} onChange={onChange} style={inputStyle}>
          {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      ) : (
        <input type={type} name={name} value={value || ''} onChange={onChange}
               placeholder={placeholder} style={inputStyle} required={required} />
      )}
    </div>
  );
}

function Baslik({ children }) {
  return (
    <div style={{
      fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1,
      color: C.green, borderBottom: `1px solid ${C.border}`,
      paddingBottom: 6, marginBottom: 14, marginTop: 22,
    }}>
      {children}
    </div>
  );
}

export default function HizliForm() {
  const { token } = useParams();
  const [durum, setDurum]     = useState('yukleniyor');
  const [hata, setHata]       = useState('');
  const [pdfUrl, setPdfUrl]   = useState('');
  const [profil, setProfil]   = useState({});
  const [fotograflar, setFotograflar] = useState([]);
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
        resolve({ name: dosya.name, preview: ev.target.result, b64: ev.target.result.split(',')[1] });
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

  /* ── Yükleniyor ── */
  if (durum === 'yukleniyor') return (
    <div style={{ minHeight: '100vh', background: C.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ color: C.sub, fontSize: 15 }}>Yükleniyor…</div>
    </div>
  );

  /* ── Hata ── */
  if (durum === 'hata') return (
    <div style={{ minHeight: '100vh', background: C.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }}>
      <div style={{ background: C.card, borderRadius: 16, padding: 32, maxWidth: 400, width: '100%', textAlign: 'center', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
        <div style={{ fontSize: 44, marginBottom: 12 }}>❌</div>
        <div style={{ color: C.errTxt, fontSize: 15 }}>{hata}</div>
      </div>
    </div>
  );

  /* ── Başarı ── */
  if (durum === 'basari') return (
    <div style={{ minHeight: '100vh', background: C.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }}>
      <div style={{ background: C.card, borderRadius: 16, padding: 32, maxWidth: 400, width: '100%', textAlign: 'center', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
        <div style={{ fontSize: 52, marginBottom: 12 }}>✅</div>
        <div style={{ color: C.green, fontWeight: 700, fontSize: 20, marginBottom: 8 }}>Belge hazır!</div>
        <div style={{ color: C.sub, fontSize: 14, marginBottom: 24 }}>PDF WhatsApp'ınıza gönderildi.</div>
        {pdfUrl && (
          <a href={pdfUrl} target="_blank" rel="noreferrer" style={{
            display: 'inline-block', background: C.green, color: '#fff',
            borderRadius: 10, padding: '12px 28px', textDecoration: 'none',
            fontWeight: 700, fontSize: 15,
          }}>
            📄 PDF'i Aç
          </a>
        )}
        <div style={{ color: '#9ca3af', fontSize: 12, marginTop: 20 }}>Bu pencereyi kapatabilirsiniz.</div>
      </div>
    </div>
  );

  /* ── Form ── */
  return (
    <div style={{ minHeight: '100vh', background: C.bg, padding: '20px 16px 40px' }}>
      <div style={{ maxWidth: 480, margin: '0 auto', background: C.card, borderRadius: 16, padding: '24px 20px', boxShadow: '0 2px 16px rgba(0,0,0,0.07)' }}>

        {/* Başlık */}
        <div style={{ marginBottom: 4 }}>
          <div style={{ fontSize: 22, fontWeight: 800, color: C.text }}>🏠 Yer Gösterme Formu</div>
          {profil.isletme_adi && (
            <div style={{ fontSize: 13, color: C.sub, marginTop: 2 }}>{profil.isletme_adi}</div>
          )}
        </div>

        {hata && (
          <div style={{ background: C.err, color: C.errTxt, borderRadius: 8, padding: '10px 14px', fontSize: 13, margin: '14px 0' }}>
            {hata}
          </div>
        )}

        {/* KVKK Bilgilendirme */}
        <div style={{ background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 8,
                      padding: '10px 14px', fontSize: 12, color: '#92400e', marginTop: 16, lineHeight: 1.6 }}>
          <strong>Kişisel Veri Bildirimi:</strong> Bu form aracılığıyla girilen alıcı/kiracı bilgileri
          yalnızca yer gösterme sözleşmesi belgesi oluşturmak amacıyla işlenmekte ve
          hizmet sağlayıcı emlakçıya iletilmektedir (KVKK md. 5/2-c).
        </div>

        <form onSubmit={gonder}>
          {/* Alıcı */}
          <Baslik>👤 Alıcı / Kiracı Adayı</Baslik>
          <Alan label="Ad Soyad" name="alici_ad" value={form.alici_ad}
                onChange={degistir} placeholder="Ali Veli" required />
          <Alan label="TC Kimlik No" name="alici_tc" value={form.alici_tc}
                onChange={degistir} placeholder="Opsiyonel" />
          <Alan label="Telefon" name="alici_tel" value={form.alici_tel}
                onChange={degistir} placeholder="0532 111 2222" type="tel" />

          {/* Taşınmaz */}
          <Baslik>📍 Taşınmaz</Baslik>
          <Alan label="Adres" name="adres" value={form.adres}
                onChange={degistir} placeholder="Mah. Sok. No:1 İlçe / Şehir" required />
          <Alan label="İlçe" name="ilce" value={form.ilce}
                onChange={degistir} placeholder="Kadıköy" />
          <Alan label="Şehir" name="sehir" value={form.sehir}
                onChange={degistir} placeholder="İstanbul" />

          {/* İşlem */}
          <Baslik>💰 İşlem Bilgileri</Baslik>
          <Alan label="İşlem Türü" name="islem_turu" value={form.islem_turu}
                onChange={degistir} required
                options={[{ value: 'kira', label: 'Kiralama' }, { value: 'satis', label: 'Satış' }]} />
          <Alan label="Bedel (TL)" name="fiyat" type="number" value={form.fiyat}
                onChange={degistir} placeholder="15000" required />
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

          {/* Fotoğraflar */}
          <Baslik>📸 Fotoğraflar (isteğe bağlı, max 4)</Baslik>
          {fotograflar.length > 0 && (
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
              {fotograflar.map((f, i) => (
                <div key={i} style={{ position: 'relative' }}>
                  <img src={f.preview} alt="" style={{
                    width: 76, height: 76, objectFit: 'cover', borderRadius: 8,
                    border: `2px solid ${C.border}`,
                  }} />
                  <button type="button" onClick={() => fotoCikar(i)} style={{
                    position: 'absolute', top: -6, right: -6,
                    background: '#ef4444', color: '#fff', border: 'none',
                    borderRadius: '50%', width: 22, height: 22, fontSize: 12,
                    cursor: 'pointer', lineHeight: '22px', padding: 0,
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
                width: '100%', background: C.greenL, border: `1px dashed ${C.green}`,
                color: C.green, borderRadius: 8, padding: '11px 0', fontSize: 14,
                fontWeight: 600, cursor: 'pointer', marginBottom: 14,
              }}>
                + Fotoğraf Ekle ({fotograflar.length}/4)
              </button>
            </>
          )}

          <button type="submit" disabled={durum === 'gonderiliyor'} style={{
            width: '100%', background: C.green, color: '#fff', border: 'none',
            borderRadius: 10, padding: '15px 0', fontSize: 16, fontWeight: 700,
            cursor: durum === 'gonderiliyor' ? 'not-allowed' : 'pointer',
            opacity: durum === 'gonderiliyor' ? 0.7 : 1,
            marginTop: 8,
          }}>
            {durum === 'gonderiliyor' ? '⏳ PDF hazırlanıyor…' : '📄 Belgeyi Oluştur'}
          </button>
        </form>
      </div>
    </div>
  );
}
