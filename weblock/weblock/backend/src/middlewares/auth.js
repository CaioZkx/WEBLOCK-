const jwt = require('jsonwebtoken');
const { users } = require('../models/database');

const authMiddleware = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token não fornecido.' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = users.find(u => u.id === decoded.id && u.active);
    if (!user) return res.status(401).json({ error: 'Usuário inativo ou não encontrado.' });
    req.user = user;
    next();
  } catch {
    return res.status(401).json({ error: 'Token inválido ou expirado.' });
  }
};

const adminOnly = (req, res, next) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Acesso restrito a administradores.' });
  next();
};

const adminOrProfessor = (req, res, next) => {
  if (!['admin', 'professor'].includes(req.user.role)) return res.status(403).json({ error: 'Acesso negado.' });
  next();
};

module.exports = { authMiddleware, adminOnly, adminOrProfessor };
