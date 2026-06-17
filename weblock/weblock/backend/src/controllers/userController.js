const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const { users } = require('../models/database');

const listUsers = (req, res) => {
  const { role, active, search } = req.query;
  let result = users.map(({ password: _, ...u }) => u);

  if (role) result = result.filter(u => u.role === role);
  if (active !== undefined) result = result.filter(u => u.active === (active === 'true'));
  if (search) {
    const q = search.toLowerCase();
    result = result.filter(u => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q) || u.matricula?.toLowerCase().includes(q));
  }

  res.json({ total: result.length, users: result });
};

const getUser = (req, res) => {
  const user = users.find(u => u.id === req.params.id);
  if (!user) return res.status(404).json({ error: 'Usuário não encontrado.' });
  const { password: _, ...safe } = user;
  res.json(safe);
};

const createUser = async (req, res) => {
  const { name, email, password, role, matricula } = req.body;
  if (!name || !email || !password || !role) return res.status(400).json({ error: 'Campos obrigatórios: name, email, password, role.' });

  const validRoles = ['admin', 'professor', 'aluno', 'terceirizado'];
  if (!validRoles.includes(role)) return res.status(400).json({ error: `Role inválida. Use: ${validRoles.join(', ')}` });

  if (users.find(u => u.email === email.toLowerCase().trim())) return res.status(409).json({ error: 'Email já cadastrado.' });

  const hash = await bcrypt.hash(password, parseInt(process.env.BCRYPT_ROUNDS) || 12);
  const newUser = {
    id: uuidv4(), name, email: email.toLowerCase().trim(),
    password: hash, role, matricula: matricula || null,
    active: true, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
  };
  users.push(newUser);
  const { password: _, ...safe } = newUser;
  res.status(201).json(safe);
};

const updateUser = async (req, res) => {
  const idx = users.findIndex(u => u.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Usuário não encontrado.' });

  const { name, email, password, role, matricula, active } = req.body;
  const user = users[idx];

  if (email && email !== user.email && users.find(u => u.email === email.toLowerCase().trim())) {
    return res.status(409).json({ error: 'Email já em uso.' });
  }

  if (name) user.name = name;
  if (email) user.email = email.toLowerCase().trim();
  if (role) user.role = role;
  if (matricula !== undefined) user.matricula = matricula;
  if (active !== undefined) user.active = active;
  if (password) user.password = await bcrypt.hash(password, parseInt(process.env.BCRYPT_ROUNDS) || 12);
  user.updatedAt = new Date().toISOString();

  const { password: _, ...safe } = user;
  res.json(safe);
};

const deleteUser = (req, res) => {
  const idx = users.findIndex(u => u.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Usuário não encontrado.' });
  if (users[idx].id === req.user.id) return res.status(400).json({ error: 'Não é possível remover seu próprio usuário.' });
  // Soft delete
  users[idx].active = false;
  users[idx].updatedAt = new Date().toISOString();
  res.json({ message: 'Usuário desativado com sucesso.' });
};

module.exports = { listUsers, getUser, createUser, updateUser, deleteUser };
