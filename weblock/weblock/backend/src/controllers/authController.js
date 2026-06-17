const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { users } = require('../models/database');

const login = async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'Email e senha são obrigatórios.' });

  const user = users.find(u => u.email === email.toLowerCase().trim());
  if (!user || !user.active) return res.status(401).json({ error: 'Credenciais inválidas.' });

  const valid = await bcrypt.compare(password, user.password);
  if (!valid) return res.status(401).json({ error: 'Credenciais inválidas.' });

  const token = jwt.sign(
    { id: user.id, email: user.email, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRES_IN }
  );

  const { password: _, ...safeUser } = user;
  res.json({ token, user: safeUser });
};

const getMe = (req, res) => {
  const { password: _, ...safeUser } = req.user;
  res.json(safeUser);
};

module.exports = { login, getMe };
