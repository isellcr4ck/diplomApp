const express = require('express');
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());

let currencies = [
  { code: 'USD', rate: 92.5 },
  { code: 'EUR', rate: 101.2 },
  { code: 'CNY', rate: 12.7 }
];

let history = [];

// Получить все валюты
app.get('/api/currency', (req, res) => {
  res.json(currencies);
});

// Получить историю изменений курсов (этот маршрут должен быть выше!)
app.get('/api/currency/history', (req, res) => {
  res.json(history.slice(0, 10));
});

// Получить курс по коду
app.get('/api/currency/:code', (req, res) => {
  const currency = currencies.find(c => c.code === req.params.code.toUpperCase());
  if (currency) {
    res.json(currency);
  } else {
    res.status(404).json({ error: 'Currency not found' });
  }
});

// Добавить новую валюту
app.post('/api/currency', (req, res) => {
  const { code, rate } = req.body;
  if (!code || !rate) {
    return res.status(400).json({ error: 'Code and rate are required' });
  }
  if (currencies.find(c => c.code === code.toUpperCase())) {
    return res.status(400).json({ error: 'Currency already exists' });
  }
  const newCurrency = { code: code.toUpperCase(), rate: Number(rate) };
  currencies.push(newCurrency);
  // Добавляем в историю (операция добавления)
  history.unshift({
    code: newCurrency.code,
    oldRate: null,
    newRate: newCurrency.rate,
    changedAt: new Date().toISOString(),
    action: 'add'
  });
  if (history.length > 50) history.pop();
  res.status(201).json(newCurrency);
});

// Обновить курс валюты
app.put('/api/currency/:code', (req, res) => {
  const currency = currencies.find(c => c.code === req.params.code.toUpperCase());
  if (!currency) {
    return res.status(404).json({ error: 'Currency not found' });
  }
  const { rate } = req.body;
  if (!rate) {
    return res.status(400).json({ error: 'Rate is required' });
  }
  const oldRate = currency.rate;
  currency.rate = Number(rate);
  // Добавляем в историю (операция обновления)
  history.unshift({
    code: currency.code,
    oldRate,
    newRate: currency.rate,
    changedAt: new Date().toISOString(),
    action: 'update'
  });
  if (history.length > 50) history.pop();
  res.json(currency);
});

// Удалить валюту
app.delete('/api/currency/:code', (req, res) => {
  const index = currencies.findIndex(c => c.code === req.params.code.toUpperCase());
  if (index === -1) {
    return res.status(404).json({ error: 'Currency not found' });
  }
  const deleted = currencies.splice(index, 1);
  res.json(deleted[0]);
});

app.listen(3001, () => console.log('Express API running on http://localhost:3001'));