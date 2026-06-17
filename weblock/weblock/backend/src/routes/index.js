const express = require('express');
const router = express.Router();
const { authMiddleware, adminOnly, adminOrProfessor } = require('../middlewares/auth');

// Controllers
const { login, getMe }       = require('../controllers/authController');
const { listUsers, getUser, createUser, updateUser, deleteUser } = require('../controllers/userController');
const { requestAccess, lockEvent } = require('../controllers/lockController');
const { getLogs, getLogById }      = require('../controllers/logController');
const { getAnalytics }             = require('../controllers/analyticsController');
const { listLocations, createLocation, updateLocation } = require('../controllers/locationController');

// ── Auth ─────────────────────────────────────────────────────────────────────
router.post('/auth/login', login);
router.get('/auth/me', authMiddleware, getMe);

// ── Usuários ─────────────────────────────────────────────────────────────────
router.get   ('/users',      authMiddleware, adminOrProfessor, listUsers);
router.get   ('/users/:id',  authMiddleware, getUser);
router.post  ('/users',      authMiddleware, adminOnly, createUser);
router.put   ('/users/:id',  authMiddleware, adminOnly, updateUser);
router.delete('/users/:id',  authMiddleware, adminOnly, deleteUser);

// ── Fechadura / Controle de Acesso ───────────────────────────────────────────
// Estes endpoints são chamados pelo hardware da fechadura (sem auth JWT — usa IP allowlist em produção)
router.post('/lock/access', requestAccess);
router.post('/lock/event',  lockEvent);

// ── Logs de Auditoria ────────────────────────────────────────────────────────
router.get('/logs',      authMiddleware, getLogs);
router.get('/logs/:id',  authMiddleware, getLogById);

// ── Analytics ────────────────────────────────────────────────────────────────
router.get('/analytics', authMiddleware, adminOrProfessor, getAnalytics);

// ── Locais ───────────────────────────────────────────────────────────────────
router.get ('/locations',      authMiddleware, listLocations);
router.post('/locations',      authMiddleware, adminOnly, createLocation);
router.put ('/locations/:id',  authMiddleware, adminOnly, updateLocation);

// ── Health ───────────────────────────────────────────────────────────────────
router.get('/health', (_, res) => res.json({ status: 'ok', version: '1.0.0', timestamp: new Date().toISOString() }));

module.exports = router;
