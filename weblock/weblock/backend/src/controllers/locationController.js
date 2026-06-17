const { v4: uuidv4 } = require('uuid');
const { locations } = require('../models/database');

const listLocations = (req, res) => res.json(locations.filter(l => l.active));

const createLocation = (req, res) => {
  const { name, building, floor } = req.body;
  if (!name) return res.status(400).json({ error: 'Nome é obrigatório.' });
  const loc = { id: uuidv4(), name, building: building || '', floor: floor || '', active: true, createdAt: new Date().toISOString() };
  locations.push(loc);
  res.status(201).json(loc);
};

const updateLocation = (req, res) => {
  const loc = locations.find(l => l.id === req.params.id);
  if (!loc) return res.status(404).json({ error: 'Local não encontrado.' });
  const { name, building, floor, active } = req.body;
  if (name) loc.name = name;
  if (building !== undefined) loc.building = building;
  if (floor !== undefined) loc.floor = floor;
  if (active !== undefined) loc.active = active;
  res.json(loc);
};

module.exports = { listLocations, createLocation, updateLocation };
