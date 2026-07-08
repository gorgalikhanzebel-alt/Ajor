const express = require('express');
const app = express();
app.use(express.json());

const BOT_TOKEN = process.env.BOT_TOKEN;

app.post('/webhook', (req, res) => {
  const { message } = req.body;
  if (message) {
    console.log('پیام دریافت شد:', message.text);
  }
  res.sendStatus(200);
});

app.get('/', (req, res) => {
  res.send('ربات فعال است!');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`ربات روی پورت ${PORT} اجرا شد`);
});
