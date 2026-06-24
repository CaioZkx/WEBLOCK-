import { useState, useEffect } from 'react';
import { lockAPI, usersAPI, locationsAPI } from '../services/api';
import { Lock, Unlock, Zap } from 'lucide-react';

export default function SimulatePage() {
  const [users, setUsers]         = useState([]);
  const [locations, setLocations] = useState([]);
  const [userId, setUserId]       = useState('');
  const [locationId, setLocationId] = useState('');
  const [result, setResult]       = useState(null);
  const [loading, setLoading]     = useState(false);
  const [history, setHistory]     = useState([]);

  useEffect(() => {
    usersAPI.list({ active: true }).then(r => setUsers(r.data.users));
    locationsAPI.list().then(r => setLocations(r.data));
  }, []);
const simulate = async () => {
  if (!userId || !locationId) return;
  setLoading(true);
  try {
    const realUserId = userId === 'UNKNOWN' ? null : userId;
    const cardId = userId === 'UNKNOWN' ? `CARD-${Math.floor(Math.random()*99999)}` : undefined;
    const { data } = await lockAPI.requestAccess(realUserId, locationId, cardId);
    setResult(data);
    setHistory(h => [{ ...data, ts: new Date().toLocaleTimeString('pt-BR'), userId, locationId }, ...h].slice(0, 20));
  } catch (e) { console.error(e); }
  setLoading(false);
};

  const allowed = result?.allowed;

  return (
    <div style={S.page}>
      <div style={S.header}>
        <div><h1 style={S.title}>Simular Acesso</h1><p style={S.sub}>Simula a decisão do motor de controle de acesso</p></div>
      </div>

      <div style={S.grid}>
        {/* Painel de controle */}
        <div style={S.card}>
          <h3 style={S.cardTitle}>Parâmetros da Simulação</h3>

          <label style={S.label}>Usuário</label>
        <select style={S.select} value={userId} onChange={e => setUserId(e.target.value)}>
        <option value="">Selecione um usuário...</option>
        <option value="UNKNOWN">🚫 Cartão não cadastrado (simular intruso)</option>
        {users.map(u => <option key={u.id} value={u.id}>{u.name} ({u.role})</option>)}
        </select>

          <label style={{ ...S.label, marginTop: 16 }}>Local</label>
          <select style={S.select} value={locationId} onChange={e => setLocationId(e.target.value)}>
            <option value="">Selecione um local...</option>
            {locations.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>

          <button style={{ ...S.simBtn, opacity: (!userId || !locationId || loading) ? 0.6 : 1 }}
            onClick={simulate} disabled={!userId || !locationId || loading}>
            <Zap size={18}/> {loading ? 'Processando...' : 'Simular Acesso'}
          </button>

          {result && (
            <div style={{ ...S.resultBox, background: allowed ? '#f0fdf4' : '#fef2f2', border: `2px solid ${allowed ? '#10b981' : '#ef4444'}` }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                {allowed ? <Unlock size={28} color="#10b981"/> : <Lock size={28} color="#ef4444"/>}
                <span style={{ fontSize: 20, fontWeight: 700, color: allowed ? '#059669' : '#ef4444' }}>
                  {allowed ? 'ACESSO PERMITIDO' : 'ACESSO NEGADO'}
                </span>
              </div>
              {result.user && <p style={S.rInfo}><strong>Usuário:</strong> {result.user.name} ({result.user.role})</p>}
              {result.location && <p style={S.rInfo}><strong>Local:</strong> {result.location.name}</p>}
              {result.reason && <p style={{ ...S.rInfo, color: '#ef4444' }}><strong>Motivo:</strong> {result.reason}</p>}
              <p style={{ ...S.rInfo, color: '#94a3b8' }}><strong>Tempo de resposta:</strong> {result.responseTimeMs}ms</p>
            </div>
          )}
        </div>

        {/* Histórico */}
        <div style={S.card}>
          <h3 style={S.cardTitle}>Histórico da Sessão</h3>
          {history.length === 0 ? <p style={{ color: '#94a3b8', fontSize: 14 }}>Nenhuma simulação ainda.</p> : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {history.map((h, i) => (
                <div key={i} style={{ ...S.histItem, background: h.allowed ? '#f0fdf4' : '#fef2f2', borderLeft: `4px solid ${h.allowed ? '#10b981' : '#ef4444'}` }}>
                  <span style={{ fontSize: 12, color: '#94a3b8' }}>{h.ts}</span>
                  <span style={{ fontSize: 13, fontWeight: 600, color: h.allowed ? '#059669' : '#ef4444' }}>{h.allowed ? '✅ Permitido' : '❌ Negado'}</span>
                  {h.location && <span style={{ fontSize: 12, color: '#475569' }}>{h.location.name}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const S = {
  page:      { padding: 32, fontFamily: 'Inter, sans-serif' },
  header:    { marginBottom: 28 },
  title:     { margin: 0, fontSize: 24, fontWeight: 700, color: '#0f172a' },
  sub:       { margin: '4px 0 0', color: '#64748b', fontSize: 14 },
  grid:      { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 },
  card:      { background: '#fff', borderRadius: 12, padding: '24px', border: '1px solid #e2e8f0' },
  cardTitle: { margin: '0 0 20px', fontSize: 16, fontWeight: 700, color: '#0f172a' },
  label:     { display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 6 },
  select:    { width: '100%', padding: '10px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, background: '#fff' },
  simBtn:    { width: '100%', marginTop: 20, padding: '12px', background: 'linear-gradient(135deg,#1d4ed8,#3b82f6)', color: '#fff', border: 'none', borderRadius: 8, fontSize: 15, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 },
  resultBox: { marginTop: 20, borderRadius: 12, padding: '16px 20px' },
  rInfo:     { margin: '4px 0', fontSize: 13, color: '#374151' },
  histItem:  { padding: '10px 14px', borderRadius: 8, display: 'flex', flexDirection: 'column', gap: 2 },
};
