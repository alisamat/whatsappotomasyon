import React, { useState, useEffect, useCallback } from 'react';
import Layout from './Layout';
import api from '../api';

const ISLEM_RENK = { kira: '#3b82f6', satis: '#f59e0b' };

function Filtre({ baslangic, bitis, tur, onChange, onAra }) {
  return (
    <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 20 }}>
      <input type="date" value={baslangic} onChange={e => onChange('baslangic', e.target.value)}
        style={inputStil} placeholder="Başlangıç" />
      <input type="date" value={bitis} onChange={e => onChange('bitis', e.target.value)}
        style={inputStil} placeholder="Bitiş" />
      <select value={tur} onChange={e => onChange('tur', e.target.value)} style={inputStil}>
        <option value="">Tüm İşlemler</option>
        <option value="kira">Kiralama</option>
        <option value="satis">Satış</option>
      </select>
      <button onClick={onAra} style={{
        background: '#25D366', color: '#fff', border: 'none', borderRadius: 8,
        padding: '8px 20px', fontSize: 14, fontWeight: 600, cursor: 'pointer',
      }}>Ara</button>
    </div>
  );
}

const inputStil = {
  background: '#1e293b', border: '1px solid #334155', borderRadius: 8,
  padding: '8px 12px', color: '#f1f5f9', fontSize: 13, outline: 'none',
};

function KayitKarti({ k, onPdfAc }) {
  const islemTuruLabel = k.islem_turu === 'kira' ? 'Kiralama' : 'Satış';
  const renk = ISLEM_RENK[k.islem_turu] || '#64748b';
  const tarih = k.sozlesme_tarihi || k.olusturma?.split('T')[0];

  return (
    <div style={{
      background: '#1e293b', borderRadius: 12, padding: '16px 20px',
      marginBottom: 10, border: '1px solid #334155',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
      flexWrap: 'wrap',
    }}>
      <div style={{ flex: 1, minWidth: 200 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <span style={{
            background: renk + '22', color: renk, borderRadius: 6,
            padding: '2px 8px', fontSize: 11, fontWeight: 700,
          }}>{islemTuruLabel}</span>
          <span style={{ color: '#64748b', fontSize: 12 }}>{tarih}</span>
        </div>
        <div style={{ color: '#f1f5f9', fontWeight: 600, fontSize: 15, marginBottom: 2 }}>
          {k.alici_ad_soyad || '—'}
        </div>
        <div style={{ color: '#94a3b8', fontSize: 13 }}>
          📍 {k.tasinmaz_adres || k.tasinmaz_sehir || '—'}
        </div>
        {k.fiyat && (
          <div style={{ color: '#64748b', fontSize: 12, marginTop: 4 }}>
            💰 {Number(k.fiyat).toLocaleString('tr-TR')} TL
          </div>
        )}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        {k.pdf_url && (
          <button onClick={() => onPdfAc(k.pdf_url)} style={{
            background: '#0f172a', border: '1px solid #334155', color: '#94a3b8',
            borderRadius: 8, padding: '6px 14px', fontSize: 13, cursor: 'pointer',
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
    } catch {
      setKayitlar([]);
    } finally {
      setYuk(false);
    }
  }, [araFiltre]);

  useEffect(() => { yukle(1); }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  const ara = () => {
    setAraFiltre(filtre);
    yukle(1, filtre);
  };

  const filtreGuncelle = (alan, deger) => setFiltre(f => ({ ...f, [alan]: deger }));

  const sayfaSayisi = Math.ceil(toplam / BOYUT);

  return (
    <Layout>
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f1f5f9', margin: 0 }}>
              📋 Yer Gösterme Kayıtları
            </h1>
            <p style={{ color: '#64748b', fontSize: 13, margin: '4px 0 0' }}>
              Toplam {toplam} kayıt
            </p>
          </div>
        </div>

        <Filtre
          baslangic={filtre.baslangic}
          bitis={filtre.bitis}
          tur={filtre.tur}
          onChange={filtreGuncelle}
          onAra={ara}
        />

        {yukleniyor ? (
          <div style={{ textAlign: 'center', color: '#64748b', padding: 40 }}>Yükleniyor...</div>
        ) : kayitlar.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#64748b', padding: 40, background: '#1e293b', borderRadius: 12 }}>
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
                <button
                  disabled={sayfa <= 1}
                  onClick={() => yukle(sayfa - 1)}
                  style={{ ...pageBtnStil, opacity: sayfa <= 1 ? 0.4 : 1 }}
                >‹ Önceki</button>
                <span style={{ color: '#94a3b8', padding: '6px 12px', fontSize: 13 }}>
                  {sayfa} / {sayfaSayisi}
                </span>
                <button
                  disabled={sayfa >= sayfaSayisi}
                  onClick={() => yukle(sayfa + 1)}
                  style={{ ...pageBtnStil, opacity: sayfa >= sayfaSayisi ? 0.4 : 1 }}
                >Sonraki ›</button>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
}

const pageBtnStil = {
  background: '#1e293b', border: '1px solid #334155', color: '#94a3b8',
  borderRadius: 8, padding: '6px 16px', fontSize: 13, cursor: 'pointer',
};
