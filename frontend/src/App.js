import React, { createContext, useContext, useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import api from './api';

import AnaSayfa   from './components/AnaSayfa';
import Giris      from './components/Giris';
import Kayit      from './components/Kayit';
import Panel      from './components/Panel';
import Kredi      from './components/Kredi';
import Profil     from './components/Profil';

// ── Auth Context ─────────────────────────────────────────────────────────────
export const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

function AuthProvider({ children }) {
  const [user, setUser]     = useState(null);
  const [yukleniyor, setYuk] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('wa_token');
    if (!token) { setYuk(false); return; }
    api.get('/auth/me')
      .then(r => setUser(r.data.user))
      .catch(() => localStorage.removeItem('wa_token'))
      .finally(() => setYuk(false));
  }, []);

  const girisYap = (token, userData) => {
    localStorage.setItem('wa_token', token);
    setUser(userData);
  };
  const cikisYap = () => {
    localStorage.removeItem('wa_token');
    setUser(null);
  };

  if (yukleniyor) return (
    <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:'100vh', color:'#64748b' }}>
      Yükleniyor...
    </div>
  );

  return (
    <AuthContext.Provider value={{ user, setUser, girisYap, cikisYap }}>
      {children}
    </AuthContext.Provider>
  );
}

function Koruma({ children }) {
  const { user } = useAuth();
  const loc = useLocation();
  if (!user) return <Navigate to="/giris" state={{ from: loc }} replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/"              element={<AnaSayfa />} />
          <Route path="/giris"         element={<Giris />} />
          <Route path="/kayit"         element={<Kayit />} />
          <Route path="/kayit/:token"  element={<Kayit />} />
          <Route path="/panel"         element={<Koruma><Panel /></Koruma>} />
          <Route path="/kredi"         element={<Koruma><Kredi /></Koruma>} />
          <Route path="/profil"        element={<Koruma><Profil /></Koruma>} />
          <Route path="*"              element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
