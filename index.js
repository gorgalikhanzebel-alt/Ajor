const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('ربات فعال است');
});

app.listen(3000, () => {
  console.log('🚀 ربات روی پورت 3000 اجرا شد');
});
