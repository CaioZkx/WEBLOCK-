const { accessLogs, users, locations } = require('../models/database');

const getAnalytics = (req, res) => {
  const { period = '7d' } = req.query;
  const msMap = { '24h': 86400000, '7d': 604800000, '30d': 2592000000 };
  const since = new Date(Date.now() - (msMap[period] || msMap['7d']));

  const filtered = accessLogs.filter(l => new Date(l.timestamp) >= since);

  // KPIs
  const total        = filtered.length;
  const permitidos   = filtered.filter(l => l.result === 'permitido').length;
  const negados      = filtered.filter(l => l.result === 'negado').length;
  const taxaAcesso   = total > 0 ? ((permitidos / total) * 100).toFixed(1) : 0;

  // Acessos por local
  const byLocation = {};
  filtered.forEach(l => {
    if (!byLocation[l.locationId]) byLocation[l.locationId] = { id: l.locationId, name: l.locationName, total: 0, permitidos: 0, negados: 0 };
    byLocation[l.locationId].total++;
    byLocation[l.locationId][l.result === 'permitido' ? 'permitidos' : 'negados']++;
  });

  // Acessos por role
  const byRole = {};
  filtered.forEach(l => {
    if (!l.userRole) return;
    if (!byRole[l.userRole]) byRole[l.userRole] = { role: l.userRole, total: 0 };
    byRole[l.userRole].total++;
  });

  // Acessos por hora do dia (heatmap)
  const byHour = Array.from({ length: 24 }, (_, i) => ({ hour: i, total: 0 }));
  filtered.forEach(l => {
    const h = new Date(l.timestamp).getHours();
    byHour[h].total++;
  });

  // Acessos por dia (últimos 7 dias sempre mostrado)
  const byDay = {};
  filtered.forEach(l => {
    const day = l.timestamp.split('T')[0];
    if (!byDay[day]) byDay[day] = { date: day, total: 0, permitidos: 0, negados: 0 };
    byDay[day].total++;
    byDay[day][l.result === 'permitido' ? 'permitidos' : 'negados']++;
  });

  // Usuários mais ativos
  const byUser = {};
  filtered.forEach(l => {
    if (!l.userId) return;
    if (!byUser[l.userId]) byUser[l.userId] = { userId: l.userId, name: l.userName, role: l.userRole, total: 0 };
    byUser[l.userId].total++;
  });
  const topUsers = Object.values(byUser).sort((a, b) => b.total - a.total).slice(0, 10);

  res.json({
    period,
    kpis: { total, permitidos, negados, taxaAcesso: parseFloat(taxaAcesso), totalUsuarios: users.filter(u => u.active).length, totalLocais: locations.filter(l => l.active).length },
    byLocation: Object.values(byLocation).sort((a, b) => b.total - a.total),
    byRole: Object.values(byRole).sort((a, b) => b.total - a.total),
    byHour,
    byDay: Object.values(byDay).sort((a, b) => a.date.localeCompare(b.date)),
    topUsers,
  });
};

module.exports = { getAnalytics };
