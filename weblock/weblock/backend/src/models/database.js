/**
 * WebLock - Banco de Dados em Memória
 * Em produção, substituir por PostgreSQL/MySQL com Sequelize ou Prisma.
 */

const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcryptjs');

// ─── Usuários ────────────────────────────────────────────────────────────────
const users = [];

// ─── Locais / Salas ──────────────────────────────────────────────────────────
const locations = [
  { id: 'loc-001', name: 'Laboratório de Informática 1', building: 'Bloco A', floor: '1', active: true, createdAt: new Date().toISOString() },
  { id: 'loc-002', name: 'Laboratório de Informática 2', building: 'Bloco A', floor: '2', active: true, createdAt: new Date().toISOString() },
  { id: 'loc-003', name: 'Sala de Aula 101',            building: 'Bloco B', floor: '1', active: true, createdAt: new Date().toISOString() },
  { id: 'loc-004', name: 'Biblioteca',                  building: 'Bloco C', floor: '1', active: true, createdAt: new Date().toISOString() },
  { id: 'loc-005', name: 'Sala dos Professores',        building: 'Bloco B', floor: '2', active: true, createdAt: new Date().toISOString() },
];

// ─── Logs de Acesso ──────────────────────────────────────────────────────────
const accessLogs = [];

// ─── Permissões de Acesso por Local ──────────────────────────────────────────
// Define quais roles têm acesso a quais locations
const accessPermissions = [
  { locationId: 'loc-001', roles: ['admin', 'professor', 'aluno'] },
  { locationId: 'loc-002', roles: ['admin', 'professor', 'aluno'] },
  { locationId: 'loc-003', roles: ['admin', 'professor', 'aluno', 'terceirizado'] },
  { locationId: 'loc-004', roles: ['admin', 'professor', 'aluno', 'terceirizado'] },
  { locationId: 'loc-005', roles: ['admin', 'professor'] },
];

// ─── Seed: Usuário Admin Padrão ──────────────────────────────────────────────
async function seedDatabase() {
  const passwordHash = await bcrypt.hash('admin123', 12);
  users.push({
    id: uuidv4(),
    name: 'Administrador',
    email: 'admin@weblock.ufc.br',
    password: passwordHash,
    role: 'admin',
    matricula: 'ADM0001',
    active: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  });

  // Seed alguns usuários de exemplo
  const exampleUsers = [
    { name: 'Prof. João Silva', email: 'joao.silva@ufc.br', role: 'professor', matricula: 'PROF001' },
    { name: 'Maria Oliveira',   email: 'maria.oliveira@ufc.br', role: 'aluno',     matricula: '2021001' },
    { name: 'Carlos Souza',     email: 'carlos.souza@ufc.br',   role: 'aluno',     matricula: '2022003' },
    { name: 'Ana Lima',         email: 'ana.lima@ufc.br',        role: 'terceirizado', matricula: 'TERC01' },
  ];

  for (const u of exampleUsers) {
    const hash = await bcrypt.hash('senha123', 12);
    users.push({ id: uuidv4(), ...u, password: hash, active: true, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() });
  }

  // Seed logs de acesso de exemplo (últimas 48h)
  const now = Date.now();
  const results = ['permitido', 'permitido', 'permitido', 'negado'];
  for (let i = 0; i < 30; i++) {
    const user = users[Math.floor(Math.random() * users.length)];
    const loc  = locations[Math.floor(Math.random() * locations.length)];
    const result = results[Math.floor(Math.random() * results.length)];
    accessLogs.push({
      id: uuidv4(),
      userId: user.id,
      userName: user.name,
      userRole: user.role,
      locationId: loc.id,
      locationName: loc.name,
      result,
      reason: result === 'negado' ? 'Sem permissão para este local' : null,
      timestamp: new Date(now - Math.random() * 172800000).toISOString(),
      deviceIp: `192.168.1.${Math.floor(Math.random() * 50) + 10}`,
    });
  }
  accessLogs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  console.log(`[DB] Seed concluído: ${users.length} usuários, ${accessLogs.length} logs`);
}

module.exports = { users, locations, accessLogs, accessPermissions, seedDatabase };
