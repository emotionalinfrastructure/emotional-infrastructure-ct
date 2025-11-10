const express = require('express');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

app.post('/token/validate', (req, res) => {
  try {
    const decoded = jwt.verify(req.body.token, 'secret');
    res.json({ valid: true, claims: decoded });
  } catch (e) {
    res.status(400).json({ valid: false, error: e.message });
  }
});

app.listen(3000, () => console.log('CTP validation API running'));