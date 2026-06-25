import { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Plus, Edit2, Trash2, Search } from 'lucide-react';

const ROLES = ['admin','professor','aluno','terceirizado'];
const ROLE_COLORS = { admin:'#7c3aed', professor:'#1d4ed8', aluno:'#059669', terceirizado:'#d97706' };
const empty = { name:'', email:'', password:'', role:'aluno', matricula:'', active: true };

export default function UsersPage() {
  const { isAdmin } = useAuth();
  const [users, setUsers]   = useState([]);
  const [search, setSearch] = useState('');
  const [roleF, setRoleF]   = useState('');
  const [modal, setModal]   = useState(null); // null | 'create' | user obj
  const [form, setForm]     = useState(empty);
  const [saving, setSaving] = useState(false);
  const [error, setError]   = useState('');

  const fetchUsers = async () => {
    const params = {};
    if (roleF) params.role = roleF;
    if (search) params.search = search;
    const { data } = await usersAPI.list(params);
    setUsers(data.users);
  };

  useEffect(() => { fetchUsers(); }, [search, roleF]);

  const openCreate = () => { setForm(empty); setError(''); setModal('create'); };
  const openEdit   = u => { setForm({ ...u, password: '' }); setError(''); setModal(u); };

  const save = async () => {
    setSaving(true); setError('');
    try {
      if (modal === 'create') await usersAPI.create(form);
      else await usersAPI.update(modal.id, form);
      setModal(null); fetchUsers();
    } catch (e) { setError(e.response?.data?.error || 'Erro ao salvar.'); }
    setSaving(false);
  };

const deactivate = async id => {
  if (!confirm('Excluir permanentemente este usuário? Essa ação não pode ser desfeita.')) return;
  await usersAPI.delete(id, true); fetchUsers();
};
  return (
    <div style={S.page}>
      <div style={S.header}>
        <div><h1 style={S.title}>Usuários</h1><p style={S.sub}>Gerenciamento de usuários e permissões</p></div>
        {isAdmin && <button style={S.btn} onClick={openCreate}><Plus size={16}/> Novo Usuário</button>}
      </div>

      <div style={S.card}>
        <div style={S.filters}>
          <div style={S.searchWrap}><Search size={15} color="#94a3b8" style={{ position:'absolute', left:10, top:9 }}/><input style={S.searchInput} placeholder="Buscar por nome, email..." value={search} onChange={e => setSearch(e.target.value)}/></div>
          <select style={S.select} value={roleF} onChange={e => setRoleF(e.target.value)}>
            <option value="">Todos os perfis</option>
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>

        <table style={S.table}>
          <thead><tr>{['Nome','Email','Matrícula','Perfil','Status','Ações'].map(h => <th key={h} style={S.th}>{h}</th>)}</tr></thead>
          <tbody>
            {users.map((u, i) => (
              <tr key={u.id} style={{ background: i%2===0?'#f8fafc':'#fff' }}>
                <td style={S.td}><strong>{u.name}</strong></td>
                <td style={S.td}>{u.email}</td>
                <td style={S.td}>{u.matricula || '—'}</td>
                <td style={S.td}><span style={{ ...S.role, background: ROLE_COLORS[u.role] || '#64748b' }}>{u.role}</span></td>
                <td style={S.td}><span style={{ color: u.active ? '#059669' : '#ef4444', fontWeight: 600, fontSize: 12 }}>{u.active ? '● Ativo' : '● Inativo'}</span></td>
                <td style={S.td}>
                  {isAdmin && <>
                    <button style={S.iconBtn} title="Editar" onClick={() => openEdit(u)}><Edit2 size={14}/></button>
                    <button style={{ ...S.iconBtn, color: '#ef4444' }} title="Desativar" onClick={() => deactivate(u.id)}><Trash2 size={14}/></button>
                  </>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div style={S.overlay}>
          <div style={S.modal}>
            <h2 style={{ margin:'0 0 20px', fontSize:18, fontWeight:700 }}>{modal === 'create' ? 'Novo Usuário' : 'Editar Usuário'}</h2>
            {[['Nome','name','text'],['Email','email','email'],['Senha','password','password'],['Matrícula','matricula','text']].map(([label, key, type]) => (
              <div key={key} style={{ marginBottom: 14 }}>
                <label style={S.label}>{label}{key==='password' && modal!=='create' ? ' (deixe em branco para manter)' : ''}</label>
                <input style={S.input} type={type} value={form[key]||''} onChange={e => setForm(f=>({...f,[key]:e.target.value}))}/>
              </div>
            ))}
            <div style={{ marginBottom: 14 }}>
              <label style={S.label}>Perfil</label>
              <select style={S.input} value={form.role} onChange={e => setForm(f=>({...f,role:e.target.value}))}>
                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            {modal !== 'create' && (
              <div style={{ marginBottom: 14 }}>
                <label style={S.label}>Status</label>
                <select style={S.input} value={form.active ? 'true' : 'false'} onChange={e => setForm(f=>({...f,active:e.target.value === 'true'}))}>
                  <option value="true">Ativo</option>
                  <option value="false">Inativo</option>
                </select>
              </div>
            )}
            {error && <p style={{ color:'#ef4444', fontSize:13, margin:'0 0 12px' }}>{error}</p>}
            <div style={{ display:'flex', gap:10, justifyContent:'flex-end' }}>
              <button style={S.cancelBtn} onClick={() => setModal(null)}>Cancelar</button>
              <button style={S.saveBtn} onClick={save} disabled={saving}>{saving ? 'Salvando...' : 'Salvar'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const S = {
  page:      { padding: 32, fontFamily: 'Inter, sans-serif' },
  header:    { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
  title:     { margin: 0, fontSize: 24, fontWeight: 700, color: '#0f172a' },
  sub:       { margin: '4px 0 0', color: '#64748b', fontSize: 14 },
  btn:       { display: 'flex', alignItems: 'center', gap: 6, background: '#1d4ed8', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 18px', cursor: 'pointer', fontWeight: 600, fontSize: 14 },
  card:      { background: '#fff', borderRadius: 12, border: '1px solid #e2e8f0' },
  filters:   { display: 'flex', gap: 12, padding: '16px 20px', borderBottom: '1px solid #f1f5f9' },
  searchWrap:{ position: 'relative', flex: 1 },
  searchInput:{ width: '100%', padding: '8px 12px 8px 32px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, boxSizing: 'border-box' },
  select:    { padding: '8px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14 },
  table:     { width: '100%', borderCollapse: 'collapse' },
  th:        { textAlign: 'left', padding: '10px 16px', fontSize: 12, fontWeight: 600, color: '#64748b', borderBottom: '1px solid #e2e8f0' },
  td:        { padding: '10px 16px', fontSize: 13, color: '#374151', borderBottom: '1px solid #f1f5f9' },
  role:      { padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 700, color: '#fff' },
  iconBtn:   { background: 'none', border: 'none', cursor: 'pointer', color: '#64748b', padding: '4px', marginRight: 4 },
  overlay:   { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 },
  modal:     { background: '#fff', borderRadius: 16, padding: '32px', width: 440, boxShadow: '0 20px 60px rgba(0,0,0,0.3)' },
  label:     { display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 5 },
  input:     { width: '100%', padding: '9px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, boxSizing: 'border-box' },
  cancelBtn: { padding: '9px 18px', border: '1.5px solid #e2e8f0', borderRadius: 8, background: '#fff', cursor: 'pointer', fontSize: 14 },
  saveBtn:   { padding: '9px 18px', background: '#1d4ed8', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600, fontSize: 14 },
};
