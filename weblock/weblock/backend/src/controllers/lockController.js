const { v4: uuidv4 } = require('uuid');
const { users, accessLogs, accessPermissions, locations } = require('../models/database');

/**
 * POST /api/lock/access
 * Chamado pela fechadura eletrônica para validar uma tentativa de acesso.
 * Body: { userId, locationId, deviceIp }
 */
const requestAccess = (req, res) => {
  const startTime = Date.now();
  const { userId, locationId, deviceIp } = req.body;

  if (!userId || !locationId) {
    return res.status(400).json({ allowed: false, reason: 'userId e locationId são obrigatórios.' });
  }

  const user = users.find(u => u.id === userId);
  if (!user || !user.active) {
    const log = buildLog({ userId, userName: 'Desconhecido', userRole: null, locationId, locationName: getLocationName(locationId), result: 'negado', reason: 'Usuário não encontrado ou inativo', deviceIp });
    accessLogs.unshift(log);
    return res.json({ allowed: false, reason: 'Usuário não encontrado ou inativo.', responseTimeMs: Date.now() - startTime });
  }

  const location = locations.find(l => l.id === locationId);
  if (!location || !location.active) {
    const log = buildLog({ userId: user.id, userName: user.name, userRole: user.role, locationId, locationName: 'Local desconhecido', result: 'negado', reason: 'Local não encontrado', deviceIp });
    accessLogs.unshift(log);
    return res.json({ allowed: false, reason: 'Local não encontrado ou inativo.', responseTimeMs: Date.now() - startTime });
  }

  const permission = accessPermissions.find(p => p.locationId === locationId);
  const allowed = !permission || permission.roles.includes(user.role);

  const log = buildLog({
    userId: user.id, userName: user.name, userRole: user.role,
    locationId, locationName: location.name,
    result: allowed ? 'permitido' : 'negado',
    reason: allowed ? null : 'Sem permissão para este local',
    deviceIp,
  });
  accessLogs.unshift(log);

  res.json({
    allowed,
    reason: allowed ? null : 'Sem permissão para este local.',
    user: { id: user.id, name: user.name, role: user.role },
    location: { id: location.id, name: location.name },
    responseTimeMs: Date.now() - startTime,
  });
};

/**
 * POST /api/lock/event
 * Endpoint para a fechadura enviar eventos gerais (ex: porta forçada, bateria baixa).
 */
const lockEvent = (req, res) => {
  const { locationId, eventType, deviceIp, description } = req.body;
  console.log(`[LOCK EVENT] ${eventType} @ ${locationId} | ${description}`);
  res.json({ received: true, timestamp: new Date().toISOString() });
};

function buildLog({ userId, userName, userRole, locationId, locationName, result, reason, deviceIp }) {
  return {
    id: uuidv4(), userId, userName, userRole,
    locationId, locationName, result, reason,
    timestamp: new Date().toISOString(),
    deviceIp: deviceIp || null,
  };
}

function getLocationName(locationId) {
  const l = locations.find(l => l.id === locationId);
  return l ? l.name : 'Desconhecido';
}

module.exports = { requestAccess, lockEvent };
