const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

// --- آدرس دیتابیس (اگر متغیر محیطی نبود، از این استفاده کن) ---
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://gorgalikhanzebel_db_user:ZZ8O2D3VhzPgqHxZ@cluster0.y56mkjn.mongodb.net/?appName=Cluster0';

// --- اتصال به MongoDB ---
mongoose.connect(MONGODB_URI)
  .then(() => console.log('✅ به MongoDB متصل شدیم!'))
  .catch(err => console.error('❌ خطا در اتصال به MongoDB:', err));

// --- مدل پیام‌ها ---
const messageSchema = new mongoose.Schema({
  userId: Number,
  message: String,
  date: { type: Date, default: Date.now }
});
const Message = mongoose.model('Message', messageSchema);

const BOT_TOKEN = process.env.BOT_TOKEN || '8985557733:AAGN4ZraC4fnc2PCm7eAOwAV-TkL0yl4L-Y';

// --- تابع ارسال پیام به تلگرام ---
async function sendMessage(chatId, text) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text })
    });
    return await response.json();
  } catch (error) {
    console.error('❌ خطا در ارسال پیام:', error);
  }
}

// --- Webhook ---
app.post('/webhook', async (req, res) => {
  const { message } = req.body;
  if (message && message.text) {
    const chatId = message.chat.id;
    const userMessage = message.text;
    const userId = message.from.id;
    console.log(`📩 پیام دریافت شد از ${userId}: ${userMessage}`);

    // ذخیره در دیتابیس
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
  res.send('🤖 ربات فعال است و به MongoDB متصل شد!');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 ربات روی پورت ${PORT} در حال اجراست`);
});
