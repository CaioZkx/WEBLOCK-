import { useState, useEffect } from 'react';
import { locationsAPI } from '../services/api';
import { Plus, MapPin, Edit2 } from 'lucide-react';

export default function LocationsPage() {
  const [locations, setLocations] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm]   = useState({ name: '', building: '', floor: '' });
  const [saving, setSaving] = useState(false);
  const [editId, setEditId] = useState(null);

  const fetch = async () => { const { data } = await locationsAPI.list(); setLocations(data); };
  useEffect(() => { fetch(); }, []);

  const save = async () => {
    setSaving(true);
    if (editId) await locationsAPI.update(editId, form);
    else await locationsAPI.create(form);
    setModal(false); setForm({ name:'', building:'', floor:'' }); setEditId(null); fetch();
    setSaving(false);
  };

  const openEdit = l => { setForm({ name: l.name, building: l.building, floor: l.floor }); setEditId(l.id); setModal(true); };

  return (
    <div style={S.page}>
      <div style={S.header}>
        <div><h1 style={S.title}>Locais / Fechaduras</h1><p style={S.sub}>Gerenciamento de salas e pontos de acesso</p></div>
        <button style={S.btn} onClick={() => { setForm({ name:'', building:'', floor:'' }); setEditId(null); setModal(true); }}><Plus size={16}/> Novo Local</button>
      </div>

      <div style={S.grid}>
        {locations.map(l => (
          <div key={l.id} style={S.card}>
            <div style={S.cardHead}>
              <div style={S.iconBox}><MapPin size={20} color="#3b82f6"/></div>
              <button style={S.editBtn} onClick={() => openEdit(l)}><Edit2 size={13}/></button>
            </div>
            <h3 style={S.locName}>{l.name}</h3>
            <p style={S.locSub}>{l.building} • {l.floor}º andar</p>
            <span style={{ ...S.statusBadge, background: l.active ? '#f0fdf4' : '#fef2f2', color: l.active ? '#059669' : '#ef4444' }}>{l.active ? '● Ativo' : '● Inativo'}</span>
          </div>
        ))}
      </div>

      {modal && (
        <div style={S.overlay}>
          <div style={S.modal}>
            <h2 style={{ margin:'0 0 20px', fontSize:18, fontWeight:700 }}>{editId ? 'Editar Local' : 'Novo Local'}</h2>
            {[['Nome do Local','name'],['Bloco/Prédio','building'],['Andar','floor']].map(([label, key]) => (
              <div key={key} style={{ marginBottom: 14 }}>
                <label style={S.label}>{label}</label>
                <input style={S.input} value={form[key]||''} onChange={e => setForm(f=>({...f,[key]:e.target.value}))}/>
              </div>
            ))}
            <div style={{ display:'flex', gap:10, justifyContent:'flex-end', marginTop:8 }}>
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
  statusBadge:{ fontSize: 12, fontWeight: 600, padding: '3px 10px', borderRadius: 12 },
  overlay:    { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 },
  modal:      { background: '#fff', borderRadius: 16, padding: 32, width: 400, boxShadow: '0 20px 60px rgba(0,0,0,0.3)' },
  label:      { display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 5 },
  input:      { width: '100%', padding: '9px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, boxSizing: 'border-box' },
  cancelBtn:  { padding: '9px 18px', border: '1.5px solid #e2e8f0', borderRadius: 8, background: '#fff', cursor: 'pointer', fontSize: 14 },
  saveBtn:    { padding: '9px 18px', background: '#1d4ed8', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600, fontSize: 14 },
};
