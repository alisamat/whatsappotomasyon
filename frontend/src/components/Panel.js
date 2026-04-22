import React, { useState, useEffect } from 'react';
import Layout from './Layout';
import { useAuth } from '../App';
import api from '../api';

const WA = '#25D366';

const turRenk = { masraf: '#3b82f6', kdv: '#f59e0b', odeme: '#10b981', kayit: '#8b5cf6' };

const SEKTOR_ETIKET = {
  emlak: '🏠 Emlak',
  marangoz: '🪵 Marangoz',
  tesisat: '🔧 Tesisat',
  diger: '➕ Diğer',
};

export default function Panel() {
  const { user, setUser } = useAuth();
  const [loglar, setLoglar]       = useState([]);
  const [yukleniyor, setY]        = useState(true);

  useEffect(() => {
    api.get('/auth/me').then(r => {
      setUser(r.data.user);
    }).catch(() => {});

    api.get('/panel/loglar').then(r => {
      setLoglar(r.data.loglar || []);
    }).catch(() => {}).finally(() => setY(false));
  }, []);

  const krediRenk = (user?.kredi || 0) < 3 ? '#dc2626' : (user?.kredi || 0) < 10 ? '#f59e0b' : '#15803d';

  return (
    <Layout>
      {/* Hoş geldin */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: '#0f172a', margin: '0 0 4px' }}>
          Hoş geldiniz, {user?.ad_soyad?.split(' ')[0]} 👋
        </h1>
        <p style={{ color: '#64748b', fontSize: 13, margin: 0 }}>
          {SEKTOR_ETIKET[user?.sektor] || user?.sektor} · {user?.telefon}
        </p>
      </div>

      {/* Üst kartlar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 32 }}>
        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.06)', borderLeft: `4px solid ${krediRenk}` }}>
          <div style={{ fontSize: 12, color: '#64748b', fontWeight: 600, marginBottom: 4 }}>KREDİ BAKİYESİ</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: krediRenk }}>{(user?.kredi || 0).toFixed(0)}</div>
          <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>kredi</div>
        </div>
        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.06)', borderLeft: '4px solid #3b82f6' }}>
          <div style={{ fontSize: 12, color: '#64748b', fontWeight: 600, marginBottom: 4 }}>TOPLAM İŞLEM</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: '#1e293b' }}>{loglar.length}</div>
          <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>işlem</div>
        </div>
        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.06)', borderLeft: '4px solid #25D366' }}>
          <div style={{ fontSize: 12, color: '#64748b', fontWeight: 600, marginBottom: 4 }}>WHATSAPP NUMARASI</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#1e293b', marginTop: 4 }}>{user?.telefon || '-'}</div>
          <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>aktif numara</div>
        </div>
      </div>

      {/* Nasıl Kullanılır */}
      <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 12, padding: 20, marginBottom: 32 }}>
        <div style={{ fontWeight: 700, color: '#15803d', fontSize: 15, marginBottom: 12 }}>
          📱 Nasıl Kullanılır?
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {[
            { adim: '1', ikon: '📸', metin: 'WhatsApp\'tan mülkün fotoğraflarını gönderin (1–3 adet)' },
            { adim: '2', ikon: '📍', metin: 'Ardından mülkün konumunu paylaşın' },
            { adim: '3', ikon: '👤', metin: 'Alıcı kişiyi rehberden gönderin' },
            { adim: '4', ikon: '📄', metin: 'Saniyeler içinde Yer Gösterme Belgesi PDF\'iniz gelir!' },
          ].map(item => (
            <div key={item.adim} style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <div style={{ background: WA, color: '#fff', borderRadius: '50%', width: 24, height: 24,
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: 11, fontWeight: 700, flexShrink: 0 }}>
                {item.adim}
              </div>
              <span style={{ fontSize: 13, color: '#374151' }}>{item.ikon} {item.metin}</span>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 14, padding: '10px 14px', background: '#fff', borderRadius: 8,
                      fontSize: 12, color: '#64748b', border: '1px solid #d1fae5' }}>
          💡 <strong>İpucu:</strong> "iptal" yazarak devam eden işlemi iptal edebilir, "bakiye" yazarak kredi durumunuzu öğrenebilirsiniz.
        </div>
      </div>

      {/* Son işlemler */}
      <div>
        <h2 style={{ fontSize: 16, fontWeight: 700, color: '#1e293b', marginBottom: 12 }}>Son İşlemler</h2>
        {yukleniyor ? (
          <div style={{ color: '#94a3b8', fontSize: 13, padding: 20, textAlign: 'center' }}>Yükleniyor...</div>
        ) : loglar.length === 0 ? (
          <div style={{ background: '#f8fafc', borderRadius: 12, padding: 32, textAlign: 'center',
                        color: '#94a3b8', fontSize: 13, border: '1px dashed #e2e8f0' }}>
            Henüz işlem yapılmamış. WhatsApp'tan ilk işleminizi gönderin!
          </div>
        ) : (
          <div style={{ background: '#fff', borderRadius: 12, overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            {loglar.slice(0, 20).map((log, i) => (
              <div key={log.id || i} style={{
                display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px',
                borderBottom: i < loglar.length - 1 ? '1px solid #f1f5f9' : 'none',
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 8, display: 'flex', alignItems: 'center',
                  justifyContent: 'center', fontSize: 16, flexShrink: 0,
                  background: log.basarili ? '#f0fdf4' : '#fef2f2',
                }}>
                  {log.basarili ? '✅' : '❌'}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#1e293b' }}>{log.aciklama || 'İşlem'}</div>
                  <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>
                    {log.olusturulma_tarihi ? new Date(log.olusturulma_tarihi).toLocaleString('tr-TR') : ''}
                  </div>
                </div>
                {log.kredi_kullanimi != null && (
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#dc2626' }}>
                    -{log.kredi_kullanimi} kr
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
