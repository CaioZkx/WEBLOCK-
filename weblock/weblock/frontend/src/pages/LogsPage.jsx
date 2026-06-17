import { useState, useEffect } from 'react';
import { logsAPI, locationsAPI } from '../services/api';
import { Search, Filter, CheckCircle, XCircle } from 'lucide-react';

export default function LogsPage() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ result: '', search: '' });

  const fetchLogs = async (p = page) => {
    setLoading(true);
    try {
      const params = { page: p, limit: 20 };
      if (filters.result) params.result = filters.result;
      const { data } = await logsAPI.list(params);
      setLogs(data.logs);
      setTotal(data.total);
      setPages(data.pages);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchLogs(1); setPage(1); }, [filters.result]);

  const fmt = ts => new Date(ts).toLocaleString('pt-BR');

  return (
    <div style={S.page}>
      <div style={S.header}>
        <div><h1 style={S.title}>Logs de Acesso</h1><p style={S.sub}>Auditoria completa de acessos</p></div>
        <span style={S.badge}>{total} registros</span>
      </div>

      <div style={S.card}>
        <div style={S.filters}>
          <select style={S.select} value={filters.result} onChange={e => setFilters(f => ({ ...f, result: e.target.value }))}>
            <option value="">Todos os resultados</option>
            <option value="permitido">✅ Permitidos</option>
            <option value="negado">❌ Negados</option>
          </select>
          <button style={S.refreshBtn} onClick={() => fetchLogs(page)}>Atualizar</button>
        </div>

        {loading ? <p style={{ padding: 20, color: '#64748b' }}>Carregando...</p> : (
          <table style={S.table}>
            <thead>
              <tr>{['Data/Hora','Usuário','Perfil','Local','Resultado','Motivo'].map(h => <th key={h} style={S.th}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {logs.map((l, i) => (
                <tr key={l.id} style={{ background: i%2===0 ? '#f8fafc' : '#fff' }}>
                  <td style={S.td}>{fmt(l.timestamp)}</td>
                  <td style={S.td}>{l.userName}</td>
                  <td style={S.td}><span style={{ ...S.role, background: ROLE_COLORS[l.userRole] || '#64748b' }}>{l.userRole}</span></td>
                  <td style={S.td}>{l.locationName}</td>
                  <td style={S.td}>
                    {l.result === 'permitido'
                      ? <span style={S.ok}><CheckCircle size={13}/> Permitido</span>
                      : <span style={S.deny}><XCircle size={13}/> Negado</span>}
                  </td>
                  <td style={{ ...S.td, color: '#94a3b8', fontSize: 12 }}>{l.reason || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <div style={S.pagination}>
          <button style={S.pgBtn} disabled={page <= 1} onClick={() => { setPage(p => p-1); fetchLogs(page-1); }}>← Anterior</button>
          <span style={{ fontSize: 13, color: '#64748b' }}>Página {page} de {pages}</span>
          <button style={S.pgBtn} disabled={page >= pages} onClick={() => { setPage(p => p+1); fetchLogs(page+1); }}>Próximo →</button>
        </div>
      </div>
    </div>
  );
}

const ROLE_COLORS = { admin: '#7c3aed', professor: '#1d4ed8', aluno: '#059669', terceirizado: '#d97706' };
const S = {
  page:     { padding: 32, fontFamily: 'Inter, sans-serif' },
  header:   { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
  title:    { margin: 0, fontSize: 24, fontWeight: 700, color: '#0f172a' },
  sub:      { margin: '4px 0 0', color: '#64748b', fontSize: 14 },
  badge:    { background: '#f1f5f9', padding: '6px 14px', borderRadius: 20, fontSize: 13, color: '#475569', fontWeight: 600 },
  card:     { background: '#fff', borderRadius: 12, border: '1px solid #e2e8f0' },
  filters:  { display: 'flex', gap: 12, padding: '16px 20px', borderBottom: '1px solid #f1f5f9' },
  select:   { padding: '8px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, background: '#fff' },
  refreshBtn:{ padding: '8px 16px', background: '#1d4ed8', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 13 },
  table:    { width: '100%', borderCollapse: 'collapse' },
  th:       { textAlign: 'left', padding: '10px 16px', fontSize: 12, fontWeight: 600, color: '#64748b', borderBottom: '1px solid #e2e8f0' },
  td:       { padding: '10px 16px', fontSize: 13, color: '#374151', borderBottom: '1px solid #f1f5f9' },
  role:     { padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 700, color: '#fff' },
  ok:       { display: 'inline-flex', alignItems: 'center', gap: 4, color: '#059669', fontWeight: 600, fontSize: 13 },
  deny:     { display: 'inline-flex', alignItems: 'center', gap: 4, color: '#ef4444', fontWeight: 600, fontSize: 13 },
  pagination:{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16, padding: 16 },
  pgBtn:    { padding: '6px 14px', border: '1.5px solid #e2e8f0', borderRadius: 8, background: '#fff', cursor: 'pointer', fontSize: 13, color: '#374151' },
};
