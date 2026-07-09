const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

// --- اتصال به MongoDB ---
const MONGODB_URI = process.env.MONGODB_URI;
mongoose.connect(MONGODB_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('✅ به MongoDB متصل شدیم!'))
  .catch(err => console.error('❌ خطا در اتصال به MongoDB:', err));

// --- تعریف مدل برای ذخیره پیام‌ها ---
const messageSchema = new mongoose.Schema({
  userId: Number,
  message: String,
  date: { type: Date, default: Date.now },
});
const Message = mongoose.model('Message', messageSchema);

const BOT_TOKEN = process.env.BOT_TOKEN;

// تابع ارسال پیام به تلگرام
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
    const userId = message.from.id;
    console.log(`📩 پیام دریافت شد از ${userId}: ${userMessage}`);

    // --- ذخیره پیام در MongoDB ---
    try {
      const newMessage = new Message({ userId, message: userMessage });
      await newMessage.save();
      console.log('💾 پیام در دیتابیس ذخیره شد.');
    } catch (error) {
      console.error('❌ خطا در ذخیره پیام:', error);
    }

    // پاسخ به کاربر
    await sendMessage(chatId, `✅ پیام شما: "${userMessage}" دریافت و ذخیره شد!`);
  }
  res.sendStatus(200);
});

app.get('/', (req, res) => {
  res.send('ربات فعال است و به MongoDB متصل شد!');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 ربات روی پورت ${PORT} در حال اجراست`);
});
