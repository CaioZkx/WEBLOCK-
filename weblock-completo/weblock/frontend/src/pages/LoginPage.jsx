import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Lock } from 'lucide-react';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate  = useNavigate();
  const [form, setForm]   = useState({ email: 'admin@weblock.ufc.br', password: 'admin123' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      await login(form.email, form.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao fazer login.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.bg}>
      <div style={styles.card}>
        <div style={styles.logo}>
          <Lock size={36} color="#fff" />
        </div>
        <h1 style={styles.title}>WebLock</h1>
        <p style={styles.subtitle}>Sistema de Controle de Acesso</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Email</label>
          <input style={styles.input} type="email" value={form.email}
            onChange={e => setForm(f => ({ ...f, email: e.target.value }))} required />

          <label style={styles.label}>Senha</label>
          <input style={styles.input} type="password" value={form.password}
            onChange={e => setForm(f => ({ ...f, password: e.target.value }))} required />

          {error && <p style={styles.error}>{error}</p>}

          <button style={{ ...styles.btn, opacity: loading ? 0.7 : 1 }} type="submit" disabled={loading}>
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
        <p style={styles.hint}>UFC • Engenharia da Computação – Sobral</p>
      </div>
    </div>
  );
}

const styles = {
  bg:       { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%)' },
  card:     { background: '#fff', borderRadius: 16, padding: '48px 40px', width: 380, boxShadow: '0 20px 60px rgba(0,0,0,0.4)', textAlign: 'center' },
  logo:     { width: 72, height: 72, background: 'linear-gradient(135deg,#1d4ed8,#3b82f6)', borderRadius: 20, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' },
  title:    { fontSize: 28, fontWeight: 700, color: '#0f172a', margin: '0 0 4px' },
  subtitle: { color: '#64748b', fontSize: 14, margin: '0 0 32px' },
  form:     { textAlign: 'left' },
  label:    { display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 6 },
  input:    { width: '100%', padding: '10px 14px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 15, marginBottom: 16, boxSizing: 'border-box', outline: 'none' },
  error:    { color: '#ef4444', fontSize: 13, margin: '-8px 0 12px' },
  btn:      { width: '100%', padding: '12px', background: 'linear-gradient(135deg,#1d4ed8,#3b82f6)', color: '#fff', border: 'none', borderRadius: 8, fontSize: 16, fontWeight: 600, cursor: 'pointer', marginTop: 4 },
  hint:     { marginTop: 24, fontSize: 12, color: '#94a3b8' },
};
