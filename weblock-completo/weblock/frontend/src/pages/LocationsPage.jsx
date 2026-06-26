import { useState, useEffect } from 'react';
import { locationsAPI } from '../services/api';
import { Plus, MapPin, Edit2, Trash2 } from 'lucide-react';

const ROLES = [
  { value: 'professor', label: 'Professor' },
  { value: 'aluno', label: 'Aluno' },
  { value: 'terceirizado', label: 'Terceirizado' },
];

const emptyForm = { name: '', building: '', floor: '', roles: [] };

export default function LocationsPage() {
  const [locations, setLocations] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm]   = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [editId, setEditId] = useState(null);

  const fetchLocations = async () => { const { data } = await locationsAPI.list(); setLocations(data); };
  useEffect(() => { fetchLocations(); }, []);

  const toggleRole = role => {
    setForm(f => ({
      ...f,
      roles: f.roles.includes(role) ? f.roles.filter(r => r !== role) : [...f.roles, role],
    }));
  };

  const save = async () => {
    if (!form.name.trim()) { setError('Nome do local é obrigatório.'); return; }
    setSaving(true); setError('');
    try {
      if (editId) await locationsAPI.update(editId, form);
      else await locationsAPI.create(form);
      setModal(false); setForm(emptyForm); setEditId(null);
      fetchLocations();
    } catch (e) {
      setError(e.response?.data?.detail || 'Erro ao salvar local.');
    }
    setSaving(false);
  };

  const openCreate = () => { setForm(emptyForm); setEditId(null); setError(''); setModal(true); };
  const openEdit   = l => { setForm({ name: l.name, building: l.building, floor: l.floor, roles: (l.roles || []).filter(r => r !== 'admin') }); setEditId(l.id); setError(''); setModal(true); };

  const removeLocation = async id => {
    if (!confirm('Excluir permanentemente este local? Essa ação não pode ser desfeita.')) return;
    try {
      await locationsAPI.delete(id, true);
      fetchLocations();
    } catch (e) {
      alert(e.response?.data?.detail || 'Erro ao excluir local.');
      console.error(e);
    }
  };

  return (
    <div style={S.page}>
      <div style={S.header}>
        <div><h1 style={S.title}>Locais / Fechaduras</h1><p style={S.sub}>Gerenciamento de salas e pontos de acesso</p></div>
        <button style={S.btn} onClick={openCreate}><Plus size={16}/> Novo Local</button>
      </div>

      <div style={S.grid}>
        {locations.map(l => (
          <div key={l.id} style={S.card}>
            <div style={S.cardHead}>
              <div style={S.iconBox}><MapPin size={20} color="#3b82f6"/></div>
              <div style={{ display: 'flex', gap: 4 }}>
                <button style={S.editBtn} onClick={() => openEdit(l)}><Edit2 size={13}/></button>
                <button style={{ ...S.editBtn, color: '#ef4444' }} onClick={() => removeLocation(l.id)}><Trash2 size={13}/></button>
              </div>
            </div>
            <h3 style={S.locName}>{l.name}</h3>
            {(l.building || l.floor) && (
              <p style={S.locSub}>
                {l.building}{l.building && l.floor ? ' • ' : ''}{l.floor ? `${l.floor}º andar` : ''}
              </p>
            )}
            <div style={S.rolesWrap}>
              <span style={S.adminTag}>Admin</span>
              {(l.roles || []).filter(r => r !== 'admin').map(r => (
                <span key={r} style={S.roleTag}>{ROLES.find(x => x.value === r)?.label || r}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {modal && (
        <div style={S.overlay}>
          <div style={S.modal}>
            <h2 style={{ margin:'0 0 20px', fontSize:18, fontWeight:700 }}>{editId ? 'Editar Local' : 'Novo Local'}</h2>

            <label style={S.label}>Nome do Local *</label>
            <input style={S.input} value={form.name} onChange={e => setForm(f=>({...f,name:e.target.value}))}/>

            <label style={{ ...S.label, marginTop: 14 }}>Bloco/Prédio</label>
            <input style={S.input} value={form.building} onChange={e => setForm(f=>({...f,building:e.target.value}))}/>

            <label style={{ ...S.label, marginTop: 14 }}>Andar</label>
            <input style={S.input} value={form.floor} onChange={e => setForm(f=>({...f,floor:e.target.value}))}/>

            <label style={{ ...S.label, marginTop: 14 }}>Quem pode acessar?</label>
            <p style={{ fontSize: 12, color: '#94a3b8', margin: '0 0 8px' }}>O administrador sempre tem acesso a todos os locais.</p>
            <div style={S.checkboxGrid}>
              {ROLES.map(r => (
                <label key={r.value} style={S.checkboxLabel}>
                  <input type="checkbox" checked={form.roles.includes(r.value)} onChange={() => toggleRole(r.value)} />
                  {r.label}
                </label>
              ))}
            </div>

            {error && <p style={{ color:'#ef4444', fontSize:13, margin:'12px 0 0' }}>{error}</p>}

            <div style={{ display:'flex', gap:10, justifyContent:'flex-end', marginTop:20 }}>
              <button style={S.cancelBtn} onClick={() => setModal(false)}>Cancelar</button>
              <button style={S.saveBtn} onClick={save} disabled={saving}>{saving?'Salvando...':'Salvar'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const S = {
  page:       { padding: 32, fontFamily: 'Inter, sans-serif' },
  header:     { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 },
  title:      { margin: 0, fontSize: 24, fontWeight: 700, color: '#0f172a' },
  sub:        { margin: '4px 0 0', color: '#64748b', fontSize: 14 },
  btn:        { display: 'flex', alignItems: 'center', gap: 6, background: '#1d4ed8', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 18px', cursor: 'pointer', fontWeight: 600, fontSize: 14 },
  grid:       { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 16 },
  card:       { background: '#fff', borderRadius: 12, padding: '20px', border: '1px solid #e2e8f0' },
  cardHead:   { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  iconBox:    { width: 44, height: 44, background: '#eff6ff', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center' },
  editBtn:    { background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' },
  locName:    { margin: '0 0 4px', fontSize: 15, fontWeight: 600, color: '#0f172a' },
  locSub:     { margin: '0 0 10px', fontSize: 13, color: '#64748b' },
  rolesWrap:  { display: 'flex', flexWrap: 'wrap', gap: 6 },
  roleTag:    { fontSize: 11, fontWeight: 600, background: '#eff6ff', color: '#1d4ed8', padding: '2px 8px', borderRadius: 10 },
  adminTag:   { fontSize: 11, fontWeight: 600, background: '#f5f3ff', color: '#7c3aed', padding: '2px 8px', borderRadius: 10 },
  overlay:    { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 },
  modal:      { background: '#fff', borderRadius: 16, padding: 32, width: 420, boxShadow: '0 20px 60px rgba(0,0,0,0.3)' },
  label:      { display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 5 },
  input:      { width: '100%', padding: '9px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, boxSizing: 'border-box' },
  checkboxGrid:{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 },
  checkboxLabel:{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: '#374151' },
  cancelBtn:  { padding: '9px 18px', border: '1.5px solid #e2e8f0', borderRadius: 8, background: '#fff', cursor: 'pointer', fontSize: 14 },
  saveBtn:    { padding: '9px 18px', background: '#1d4ed8', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600, fontSize: 14 },
};