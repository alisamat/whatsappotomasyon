import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../App';

const WA_YESIL = '#25D366';

export default function Layout({ children }) {
  const { user, cikisYap } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();

  const link = (to, label) => {
    const aktif = loc.pathname === to;
    return (
      <Link to={to} style={{
        color: aktif ? WA_YESIL : '#cbd5e1',
        fontWeight: aktif ? 700 : 500,
        textDecoration: 'none', fontSize: 14,
        borderBottom: aktif ? `2px solid ${WA_YESIL}` : '2px solid transparent',
        paddingBottom: 2,
      }}>{label}</Link>
    );
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* NAVBAR */}
      <nav style={{
        background: '#0f172a', color: '#fff',
        padding: '0 24px', height: 56,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        position: 'sticky', top: 0, zIndex: 100,
        boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
      }}>
        <Link to="/" style={{ color: WA_YESIL, fontWeight: 800, fontSize: 18, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 8 }}>
          💬 WA Otomasyon
        </Link>
        <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
          {user ? (<>
            {link('/panel', 'Panel')}
            {link('/kredi', 'Kredi')}
            {link('/profil', 'Profil')}
            <span style={{ color: '#64748b', fontSize: 13 }}>
              💳 {user.kredi?.toFixed(0)} kr
            </span>
            <button onClick={() => { cikisYap(); nav('/'); }}
              style={{ background:'none', border:'1px solid #334155', color:'#94a3b8',
                       borderRadius:6, padding:'4px 12px', fontSize:13, cursor:'pointer' }}>
              Çıkış
            </button>
          </>) : (<>
            {link('/giris', 'Giriş')}
            <Link to="/kayit" style={{
              background: WA_YESIL, color: '#fff', borderRadius: 6,
              padding: '6px 14px', fontSize: 13, fontWeight: 700, textDecoration: 'none',
            }}>Kayıt Ol</Link>
          </>)}
        </div>
      </nav>

      {/* İÇERİK */}
      <main style={{ flex: 1, maxWidth: 960, margin: '0 auto', width: '100%', padding: '32px 16px' }}>
        {children}
      </main>

      {/* FOOTER */}
      <footer style={{ background: '#0f172a', color: '#475569', textAlign: 'center', fontSize: 12, padding: '16px 0' }}>
        © 2026 WhatsApp Otomasyon · Tüm hakları saklıdır
      </footer>
    </div>
  );
}
