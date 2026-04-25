import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../App';

const G = '#25D366';

export default function Layout({ children }) {
  const { user, cikisYap } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const p = loc.pathname;

  const NavLink = ({ to, label }) => (
    <Link to={to} style={{
      color: p === to ? G : '#475569',
      fontWeight: p === to ? 700 : 500,
      textDecoration: 'none',
      fontSize: 14,
      borderBottom: p === to ? `2px solid ${G}` : '2px solid transparent',
      paddingBottom: 2,
      whiteSpace: 'nowrap',
    }}>{label}</Link>
  );

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#f8fafc' }}>

      {/* ── NAVBAR ── */}
      <nav style={{
        background: '#fff',
        borderBottom: '1px solid #e2e8f0',
        padding: '0 20px',
        height: 56,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
      }}>
        <Link to="/" style={{ color: G, fontWeight: 800, fontSize: 17, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 7 }}>
          💬 WA Otomasyon
        </Link>

        {/* Desktop nav links */}
        <div className="hide-mobile" style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
          {user ? (<>
            <NavLink to="/panel" label="Panel" />
            <NavLink to="/kredi" label="Kredi" />
            <NavLink to="/profil" label="Profil" />
            {user.sektor === 'emlak' && <NavLink to="/emlak-profil" label="Emlak" />}
            {user.sektor === 'emlak' && <NavLink to="/yer-gostermeler" label="Kayıtlar" />}
            <span style={{ color: '#15803d', fontSize: 12, background: '#f0fdf4', padding: '3px 8px', borderRadius: 20, border: '1px solid #bbf7d0' }}>
              💳 {(user.kredi || 0).toFixed(0)} kr
            </span>
            <button onClick={() => { cikisYap(); nav('/'); }} style={{
              background: 'none', border: '1px solid #e2e8f0', color: '#64748b',
              borderRadius: 6, padding: '4px 12px', fontSize: 13, cursor: 'pointer',
            }}>Çıkış</button>
          </>) : (<>
            <NavLink to="/giris" label="Giriş" />
            <Link to="/kayit" style={{
              background: G, color: '#fff', borderRadius: 6,
              padding: '6px 14px', fontSize: 13, fontWeight: 700, textDecoration: 'none',
            }}>Kayıt Ol</Link>
          </>)}
        </div>

        {/* Mobile: sadece kredi */}
        <div className="show-mobile" style={{ alignItems: 'center', gap: 10 }}>
          {user ? (
            <span style={{ color: '#15803d', fontSize: 12, background: '#f0fdf4', padding: '3px 10px', borderRadius: 20, border: '1px solid #bbf7d0', fontWeight: 600 }}>
              💳 {(user.kredi || 0).toFixed(0)} kr
            </span>
          ) : (
            <Link to="/giris" style={{ color: G, fontWeight: 700, fontSize: 14, textDecoration: 'none' }}>Giriş</Link>
          )}
        </div>
      </nav>

      {/* ── İÇERİK ── */}
      <main className="layout-main" style={{ flex: 1, maxWidth: 960, margin: '0 auto', width: '100%', padding: '24px 16px 32px' }}>
        {children}
      </main>

      {/* ── FOOTER (desktop only) ── */}
      <footer className="hide-mobile" style={{ background: '#fff', borderTop: '1px solid #e2e8f0', color: '#94a3b8', textAlign: 'center', fontSize: 12, padding: '14px 0' }}>
        © 2026 WhatsApp Otomasyon — Promis Web Hizmetleri Ltd. Şti.
      </footer>

      {/* ── BOTTOM NAV (mobile only) ── */}
      {user && (
        <nav className="bottom-nav">
          <Link to="/panel" className={p === '/panel' ? 'aktif' : ''}>
            <span className="ikon">🏠</span>Panel
          </Link>
          <Link to="/kredi" className={p === '/kredi' ? 'aktif' : ''}>
            <span className="ikon">💳</span>Kredi
          </Link>
          {user.sektor === 'emlak' && (
            <Link to="/emlak-profil" className={p === '/emlak-profil' ? 'aktif' : ''}>
              <span className="ikon">🏢</span>Profil
            </Link>
          )}
          {user.sektor === 'emlak' && (
            <Link to="/yer-gostermeler" className={p === '/yer-gostermeler' ? 'aktif' : ''}>
              <span className="ikon">📋</span>Kayıtlar
            </Link>
          )}
          <Link to="/profil" className={p === '/profil' ? 'aktif' : ''}>
            <span className="ikon">👤</span>Hesap
          </Link>
          <button onClick={() => { cikisYap(); nav('/'); }}>
            <span className="ikon">🚪</span>Çıkış
          </button>
        </nav>
      )}
    </div>
  );
}
