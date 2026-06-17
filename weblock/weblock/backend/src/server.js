require('dotenv').config();
const express = require('express');
const cors    = require('cors');
const morgan  = require('morgan');
const { seedDatabase } = require('./models/database');
const routes = require('./routes');

const app  = express();
const PORT = process.env.PORT || 3001;

// ── Middlewares ───────────────────────────────────────────────────────────────
app.use(cors({ origin: ['http://localhost:3000', 'http://localhost:5173'], credentials: true }));
app.use(express.json());
app.use(morgan('dev'));

// ── Rotas ─────────────────────────────────────────────────────────────────────
app.use('/api', routes);

// ── 404 ───────────────────────────────────────────────────────────────────────
app.use((_, res) => res.status(404).json({ error: 'Rota não encontrada.' }));

// ── Error handler ─────────────────────────────────────────────────────────────
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Erro interno do servidor.' });
});

// ── Start ─────────────────────────────────────────────────────────────────────
seedDatabase().then(() => {
  app.listen(PORT, () => {
    console.log(`\n🔒 WebLock API rodando em http://localhost:${PORT}`);
    console.log(`   Credenciais padrão: admin@weblock.ufc.br / admin123\n`);
  });
});
