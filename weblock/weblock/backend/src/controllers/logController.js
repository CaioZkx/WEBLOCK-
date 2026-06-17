const { accessLogs } = require('../models/database');

const getLogs = (req, res) => {
  const { userId, locationId, result, startDate, endDate, page = 1, limit = 50 } = req.query;

  let logs = [...accessLogs];

  if (userId)     logs = logs.filter(l => l.userId === userId);
  if (locationId) logs = logs.filter(l => l.locationId === locationId);
  if (result)     logs = logs.filter(l => l.result === result);
  if (startDate)  logs = logs.filter(l => new Date(l.timestamp) >= new Date(startDate));
  if (endDate)    logs = logs.filter(l => new Date(l.timestamp) <= new Date(endDate));

  const total = logs.length;
  const start = (parseInt(page) - 1) * parseInt(limit);
  const paginated = logs.slice(start, start + parseInt(limit));

  res.json({ total, page: parseInt(page), limit: parseInt(limit), pages: Math.ceil(total / parseInt(limit)), logs: paginated });
};

const getLogById = (req, res) => {
  const log = accessLogs.find(l => l.id === req.params.id);
  if (!log) return res.status(404).json({ error: 'Log não encontrado.' });
  res.json(log);
};

module.exports = { getLogs, getLogById };
