import { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Users, CheckCircle, XCircle, DoorOpen, TrendingUp } from 'lucide-react';

const PERIODS = [{ v: '24h', l: 'Últimas 24h' }, { v: '7d', l: 'Últimos 7 dias' }, { v: '30d', l: 'Últimos 30 dias' }];
const COLORS = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6'];
const ROLE_LABEL = { admin: 'Admin', professor: 'Professor', aluno: 'Aluno', terceirizado: 'Terceirizado' };

export default function DashboardPage() {
  const [data, setData]     = useState(null);
  const [period, setPeriod] = useState('7d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    analyticsAPI.get(period).then(r => { setData(r.data); setLoading(false); }).catch(() => setLoading(false));
  }, [period]);

  if (loading) return <div style={S.loading}>Carregando dados...</div>;
  if (!data)   return <div style={S.loading}>Erro ao carregar dados.</div>;

  const { kpis, byLocation, byRole, byDay, byHour, topUsers } = data;

  return (
    <div style={S.page}>
      <div style={S.header}>
        <div>
          <h1 style={S.title}>Dashboard</h1>
          <p style={S.sub}>Visão geral dos acessos</p>
        </div>
        <div style={S.periodBtns}>
          {PERIODS.map(p => (
            <button key={p.v} onClick={() => setPeriod(p.v)}
              style={{ ...S.periodBtn, ...(period === p.v ? S.periodActive : {}) }}>{p.l}</button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div style={S.kpiGrid}>
        <KpiCard icon={<DoorOpen size={22} color="#3b82f6"/>} label="Total de Acessos" value={kpis.total} color="#eff6ff" />
        <KpiCard icon={<CheckCircle size={22} color="#10b981"/>} label="Permitidos" value={kpis.permitidos} color="#f0fdf4" />
        <KpiCard icon={<XCircle size={22} color="#ef4444"/>} label="Negados" value={kpis.negados} color="#fef2f2" />
        <KpiCard icon={<TrendingUp size={22} color="#8b5cf6"/>} label="Taxa de Acesso" value={`${kpis.taxaAcesso}%`} color="#f5f3ff" />
        <KpiCard icon={<Users size={22} color="#f59e0b"/>} label="Usuários Ativos" value={kpis.totalUsuarios} color="#fffbeb" />
      </div>

      {/* Charts Row 1 */}
      <div style={S.row2}>
        <ChartCard title="Acessos por Dia">
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={byDay}>
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={d => d.slice(5)} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="permitidos" stroke="#10b981" strokeWidth={2} dot={false} name="Permitidos" />
              <Line type="monotone" dataKey="negados"    stroke="#ef4444" strokeWidth={2} dot={false} name="Negados" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Acessos por Perfil">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={byRole.map(r => ({ ...r, name: ROLE_LABEL[r.role] || r.role }))} dataKey="total" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}>
                {byRole.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Charts Row 2 */}
      <div style={S.row2}>
        <ChartCard title="Locais Mais Acessados">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={byLocation.slice(0,5)} layout="vertical">
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={140} />
              <Tooltip />
              <Bar dataKey="permitidos" fill="#3b82f6" name="Permitidos" stackId="a" />
              <Bar dataKey="negados"    fill="#ef4444" name="Negados"    stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Acessos por Hora do Dia">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={byHour}>
              <XAxis dataKey="hour" tick={{ fontSize: 10 }} tickFormatter={h => `${h}h`} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip labelFormatter={h => `${h}:00`} />
              <Bar dataKey="total" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Top Users */}
      <div style={S.card}>
        <h3 style={S.cardTitle}>Usuários Mais Ativos</h3>
        <table style={S.table}>
          <thead><tr>{['Nome','Perfil','Acessos'].map(h => <th key={h} style={S.th}>{h}</th>)}</tr></thead>
          <tbody>
            {topUsers.map((u, i) => (
              <tr key={u.userId} style={{ background: i % 2 === 0 ? '#f8fafc' : '#fff' }}>
                <td style={S.td}>{u.name}</td>
                <td style={S.td}><span style={{ ...S.badge, background: COLORS[['admin','professor','aluno','terceirizado'].indexOf(u.role)] || '#64748b' }}>{ROLE_LABEL[u.role] || u.role}</span></td>
                <td style={S.td}><strong>{u.total}</strong></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function KpiCard({ icon, label, value, color }) {
  return (
    <div style={{ ...S.kpiCard, background: color }}>
      <div style={S.kpiIcon}>{icon}</div>
      <div>
        <p style={S.kpiLabel}>{label}</p>
        <p style={S.kpiValue}>{value}</p>
      </div>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div style={{ ...S.card, flex: 1 }}>
      <h3 style={S.cardTitle}>{title}</h3>
      {children}
    </div>
  );
}

const S = {
  page:        { padding: 32, fontFamily: 'Inter, sans-serif' },
  loading:     { display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh', fontSize: 16, color: '#64748b' },
  header:      { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 },
  title:       { margin: 0, fontSize: 24, fontWeight: 700, color: '#0f172a' },
  sub:         { margin: '4px 0 0', color: '#64748b', fontSize: 14 },
  periodBtns:  { display: 'flex', gap: 8 },
  periodBtn:   { padding: '6px 14px', border: '1.5px solid #e2e8f0', borderRadius: 8, background: '#fff', cursor: 'pointer', fontSize: 13, color: '#64748b' },
  periodActive:{ background: '#1d4ed8', color: '#fff', borderColor: '#1d4ed8' },
  kpiGrid:     { display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 16, marginBottom: 24 },
  kpiCard:     { borderRadius: 12, padding: '18px 20px', display: 'flex', alignItems: 'center', gap: 14, border: '1px solid #e2e8f0' },
  kpiIcon:     { width: 44, height: 44, background: '#fff', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' },
  kpiLabel:    { margin: 0, fontSize: 12, color: '#64748b', fontWeight: 500 },
  kpiValue:    { margin: '2px 0 0', fontSize: 22, fontWeight: 700, color: '#0f172a' },
  row2:        { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 },
  card:        { background: '#fff', borderRadius: 12, padding: '20px 24px', border: '1px solid #e2e8f0', marginBottom: 20 },
  cardTitle:   { margin: '0 0 16px', fontSize: 15, fontWeight: 600, color: '#0f172a' },
  table:       { width: '100%', borderCollapse: 'collapse' },
  th:          { textAlign: 'left', padding: '8px 12px', fontSize: 12, fontWeight: 600, color: '#64748b', borderBottom: '1px solid #e2e8f0' },
  td:          { padding: '10px 12px', fontSize: 14, color: '#374151', borderBottom: '1px solid #f1f5f9' },
  badge:       { padding: '2px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700, color: '#fff' },
};
