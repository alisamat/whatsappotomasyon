import React, { useState, useEffect, useCallback } from 'react';
import Layout from './Layout';
import api from '../api';

const ISLEM_RENK = { kira: '#3b82f6', satis: '#f59e0b' };

const inputSt = {
  background: '#fff', border: '1px solid #d1d5db', borderRadius: 8,
  padding: '9px 12px', color: '#0f172a', fontSize: 14, outline: 'none',
  width: '100%', boxSizing: 'border-box',
};

function Filtre({ baslangic, bitis, tur, onChange, onAra }) {
  return (
    <div style={{ background: '#fff', borderRadius: 12, padding: '14px 16px', marginBottom: 16, boxShadow: '0 2px 6px rgba(0,0,0,0.05)' }}>
      <div className="grid-2" style={{ marginBottom: 10 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, color: '#6b7280', marginBottom: 4 }}>BAŞLANGIÇ</div>
          <input type="date" value={baslangic} onChange={e => onChange('baslangic', e.target.value)} style={inputSt} />
        </div>
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, color: '#6b7280', marginBottom: 4 }}>BİTİŞ</div>
          <input type="date" value={bitis} onChange={e => onChange('bitis', e.target.value)} style={inputSt} />
        </div>
      </div>
      <div style={{ display: 'flex', gap: 10 }}>
        <select value={tur} onChange={e => onChange('tur', e.target.value)} style={{ ...inputSt, flex: 1 }}>
          <option value="">Tüm İşlemler</option>
          <option value="kira">Kiralama</option>
          <option value="satis">Satış</option>
        </select>
        <button onClick={onAra} style={{
          background: '#25D366', color: '#fff', border: 'none', borderRadius: 8,
          padding: '9px 20px', fontSize: 14, fontWeight: 600, cursor: 'pointer', flexShrink: 0,
        }}>Ara</button>
      </div>
    </div>
  );
}

function KayitKarti({ k, onPdfAc }) {
  const islemLabel = k.islem_turu === 'kira' ? 'Kiralama' : 'Satış';
  const renk = ISLEM_RENK[k.islem_turu] || '#64748b';
  const tarih = k.sozlesme_tarihi || k.olusturma?.split('T')[0];

  return (
    <div style={{
      background: '#fff', borderRadius: 12, padding: '14px 16px', marginBottom: 10,
      boxShadow: '0 2px 6px rgba(0,0,0,0.05)', borderLeft: `3px solid ${renk}`,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
            <span style={{ background: renk + '18', color: renk, borderRadius: 6, padding: '2px 8px', fontSize: 11, fontWeight: 700 }}>{islemLabel}</span>
            <span style={{ color: '#94a3b8', fontSize: 12 }}>{tarih}</span>
          </div>
          <div style={{ color: '#0f172a', fontWeight: 700, fontSize: 15, marginBottom: 3 }}>
            {k.alici_ad_soyad || '—'}
          </div>
          <div style={{ color: '#64748b', fontSize: 13 }}>
            📍 {k.tasinmaz_adres || k.tasinmaz_sehir || '—'}
          </div>
          {k.fiyat && (
            <div style={{ color: '#94a3b8', fontSize: 12, marginTop: 4 }}>
              💰 {Number(k.fiyat).toLocaleString('tr-TR')} TL
            </div>
          )}
        </div>
        {k.pdf_url && (
          <button onClick={() => onPdfAc(k.pdf_url)} style={{
            background: '#f0fdf4', border: '1px solid #bbf7d0', color: '#15803d',
            borderRadius: 8, padding: '7px 14px', fontSize: 13, cursor: 'pointer', flexShrink: 0, fontWeight: 600,
          }}>📄 PDF</button>
        )}
      </div>
    </div>
  );
}

export default function YerGostermeler() {
  const [kayitlar, setKayitlar] = useState([]);
  const [toplam, setToplam]     = useState(0);
  const [sayfa, setSayfa]       = useState(1);
  const [yukleniyor, setYuk]    = useState(false);
  const [filtre, setFiltre]     = useState({ baslangic: '', bitis: '', tur: '' });
  const [araFiltre, setAraFiltre] = useState({ baslangic: '', bitis: '', tur: '' });
  const BOYUT = 10;

  const yukle = useCallback(async (sf = 1, f = araFiltre) => {
    setYuk(true);
    try {
      const params = { sayfa: sf, boyut: BOYUT };
      if (f.tur)       params.islem_turu = f.tur;
      if (f.baslangic) params.baslangic  = f.baslangic;
      if (f.bitis)     params.bitis      = f.bitis;
      const r = await api.get('/raporlar/yer-gostermeler', { params });
      setKayitlar(r.data.kayitlar || []);
      setToplam(r.data.toplam || 0);
      setSayfa(sf);
    } catch { setKayitlar([]); }
    finally { setYuk(false); }
  }, [araFiltre]);

  useEffect(() => { yukle(1); }, []); // eslint-disable-line

  const ara = () => { setAraFiltre(filtre); yukle(1, filtre); };
  const filtreGuncelle = (alan, deger) => setFiltre(f => ({ ...f, [alan]: deger }));
  const sayfaSayisi = Math.ceil(toplam / BOYUT);

  return (
    <Layout>
      <div style={{ maxWidth: 720, margin: '0 auto' }}>
        <div style={{ marginBottom: 20 }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: '#0f172a', margin: '0 0 4px' }}>
            📋 Yer Gösterme Kayıtları
          </h1>
          <p style={{ color: '#64748b', fontSize: 13, margin: 0 }}>Toplam {toplam} kayıt</p>
        </div>

        <Filtre baslangic={filtre.baslangic} bitis={filtre.bitis} tur={filtre.tur}
                onChange={filtreGuncelle} onAra={ara} />

        {yukleniyor ? (
          <div style={{ textAlign: 'center', color: '#94a3b8', padding: 40 }}>Yükleniyor…</div>
        ) : kayitlar.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#94a3b8', padding: 40, background: '#fff', borderRadius: 12, boxShadow: '0 2px 6px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>📭</div>
            Henüz kayıt yok
          </div>
        ) : (
          <>
            {kayitlar.map(k => (
              <KayitKarti key={k.id} k={k} onPdfAc={url => window.open(url, '_blank')} />
            ))}

            {sayfaSayisi > 1 && (
              <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 20 }}>
                <button disabled={sayfa <= 1} onClick={() => yukle(sayfa - 1)} style={{
                  background: '#fff', border: '1px solid #e2e8f0', color: '#374151',
                  borderRadius: 8, padding: '8px 18px', fontSize: 13, cursor: 'pointer',
                  opacity: sayfa <= 1 ? 0.4 : 1,
                }}>‹ Önceki</button>
                <span style={{ color: '#64748b', padding: '8px 12px', fontSize: 13 }}>
                  {sayfa} / {sayfaSayisi}
                </span>
                <button disabled={sayfa >= sayfaSayisi} onClick={() => yukle(sayfa + 1)} style={{
                  background: '#fff', border: '1px solid #e2e8f0', color: '#374151',
                  borderRadius: 8, padding: '8px 18px', fontSize: 13, cursor: 'pointer',
                  opacity: sayfa >= sayfaSayisi ? 0.4 : 1,
                }}>Sonraki ›</button>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
}
