import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LayoutDashboard, Users, ClipboardList, BarChart2, MapPin, Lock, LogOut, Shield } from 'lucide-react';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/logs',       icon: ClipboardList,  label: 'Logs de Acesso' },
  { to: '/users',      icon: Users,          label: 'Usuários', adminOnly: false, profOk: true },
  { to: '/locations',  icon: MapPin,         label: 'Locais',   adminOnly: true },
  { to: '/simulate',   icon: Lock,           label: 'Simular Acesso' },
];

export default function Layout({ children }) {
  const { user, logout, isAdmin, isAdminOrProf } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/login'); };

  const roleLabel = { admin: 'Administrador', professor: 'Professor', aluno: 'Aluno', terceirizado: 'Terceirizado' };
  const roleColor = { admin: '#7c3aed', professor: '#1d4ed8', aluno: '#059669', terceirizado: '#d97706' };

  return (
    <div style={S.root}>
      {/* Sidebar */}
      <aside style={S.sidebar}>
        <div style={S.logoBox}>
          <Shield size={28} color="#60a5fa" />
          <span style={S.logoText}>WebLock</span>
        </div>

        <nav style={S.nav}>
          {navItems.map(({ to, icon: Icon, label, adminOnly, profOk }) => {
            if (adminOnly && !isAdmin) return null;
            if (profOk === true && !isAdminOrProf) return null;
            return (
              <NavLink key={to} to={to} style={({ isActive }) => ({ ...S.navItem, ...(isActive ? S.navActive : {}) })}>
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div style={S.userBox}>
          <div style={{ ...S.roleBadge, background: roleColor[user?.role] || '#64748b' }}>
            {roleLabel[user?.role] || user?.role}
          </div>
          <p style={S.userName}>{user?.name}</p>
          <p style={S.userEmail}>{user?.email}</p>
          <button onClick={handleLogout} style={S.logoutBtn}>
            <LogOut size={14} /> Sair
          </button>
        </div>
      </aside>

      {/* Content */}
      <main style={S.main}>{children}</main>
    </div>
  );
}

const S = {
  root:     { display: 'flex', minHeight: '100vh', fontFamily: 'Inter, sans-serif' },
  sidebar:  { width: 240, background: '#0f172a', display: 'flex', flexDirection: 'column', padding: '24px 0', flexShrink: 0 },
  logoBox:  { display: 'flex', alignItems: 'center', gap: 10, padding: '0 24px 28px', borderBottom: '1px solid #1e293b' },
  logoText: { fontSize: 20, fontWeight: 700, color: '#f1f5f9' },
  nav:      { flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: 4 },
  navItem:  { display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', borderRadius: 8, color: '#94a3b8', textDecoration: 'none', fontSize: 14, fontWeight: 500, transition: 'all .15s' },
  navActive:{ background: '#1e3a5f', color: '#60a5fa' },
  userBox:  { padding: '20px 24px', borderTop: '1px solid #1e293b' },
  roleBadge:{ display: 'inline-block', padding: '2px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700, color: '#fff', marginBottom: 8 },
  userName: { margin: 0, fontSize: 13, fontWeight: 600, color: '#e2e8f0' },
  userEmail:{ margin: '2px 0 10px', fontSize: 11, color: '#64748b' },
  logoutBtn:{ display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: '1px solid #334155', borderRadius: 6, color: '#94a3b8', padding: '6px 12px', cursor: 'pointer', fontSize: 12 },
  main:     { flex: 1, background: '#f8fafc', overflowY: 'auto' },
};
