const express = require('express');
const app = express();
app.use(express.json());

const BOT_TOKEN = process.env.BOT_TOKEN;

// تابع برای ارسال پیام به تلگرام
async function sendMessage(chatId, text) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chatId, text: text })
  });
  return response.json();
}

app.post('/webhook', async (req, res) => {
  const { message } = req.body;
  if (message && message.text) {
    const chatId = message.chat.id;
    const userMessage = message.text;
    
    console.log(`پیام دریافت شد: ${userMessage}`);
    
    // جواب دادن به پیام
    await sendMessage(chatId, `سلام! پیام شما: "${userMessage}" رو دریافت کردم!`);
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
