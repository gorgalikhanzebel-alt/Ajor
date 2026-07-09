const express = require('express');
const mongoose = require('mongoose');
const fetch = require('node-fetch');
const app = express();
app.use(express.json());

// ===== تنظیمات با مقدار پیش‌فرض (اگر متغیر محیطی نبود) =====
const BOT_TOKEN = process.env.BOT_TOKEN || '8985557733:AAGN4ZraC4fnc2PCm7eAOwAV-TkL0yl4L-Y';
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://gorgalikhanzebel_db_user:ZZ8O2D3VhzPgqHxZ@cluster0.y56mkjn.mongodb.net/?appName=Cluster0';

// ===== اتصال به دیتابیس =====
mongoose.connect(MONGODB_URI)
  .then(() => console.log('✅ به MongoDB متصل شدیم!'))
  .catch(err => console.error('❌ خطا در اتصال به MongoDB:', err));

// ===== مدل کاربر =====
const UserSchema = new mongoose.Schema({
  userId: Number,
  username: String,
  firstName: String,
  messagesCount: { type: Number, default: 0 }
});
const User = mongoose.model('User', UserSchema);

// ===== تابع ارسال پیام =====
async function sendMessage(chatId, text, extra = {}) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
  try {
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text, parse_mode: 'Markdown', ...extra })
    });
  } catch (e) {
    console.error('❌ خطا در ارسال:', e);
  }
}

// ===== یک Webhook واحد =====
app.post('/webhook', async (req, res) => {
  const { message, callback_query } = req.body;

  // --- مدیریت دکمه‌ها ---
  if (callback_query) {
    const chatId = callback_query.message.chat.id;
    const data = callback_query.data;
    let reply = '';
    if (data === 'help') reply = '📖 راهنما: /help';
    else if (data === 'about') reply = '🤖 ربات فوق‌العاده';
    else if (data === 'joke') reply = '😂 جوک: همه جا null هست!';
    else if (data === 'quote') reply = '💪 موفقیت با تلاش به دست میاد.';
    else reply = '❌ گزینه نامعتبر';
    await sendMessage(chatId, reply);
    return res.sendStatus(200);
  }

  // --- مدیریت پیام‌ها ---
  if (message && message.text) {
    const chatId = message.chat.id;
    const userId = message.from.id;
    const text = message.text;
    const firstName = message.from.first_name || 'کاربر';

    // ثبت در دیتابیس
    try {
      await User.findOneAndUpdate(
        { userId },
        { $set: { username: message.from.username, firstName }, $inc: { messagesCount: 1 } },
        { upsert: true }
      );
    } catch (e) {}

    let reply = '';
    let keyboard = null;

    if (text === '/start') {
      keyboard = {
        inline_keyboard: [
          [{ text: '📖 راهنما', callback_data: 'help' }, { text: 'ℹ️ درباره', callback_data: 'about' }],
          [{ text: '😂 جوک', callback_data: 'joke' }, { text: '💪 نقل قول', callback_data: 'quote' }]
        ]
      };
      reply = `👋 سلام ${firstName}! خوش آمدی.`;
    } else if (text === '/help') {
      reply = '📖 راهنما: /start , /help , /about , /ping';
    } else if (text === '/about') {
      reply = '🤖 ربات فوق‌العاده';
    } else if (text === '/ping') {
      reply = '🏓 پُنگ!';
    } else if (text === '/joke') {
      reply = '😂 چرا برنامه‌نویس‌ها عاشق طبیعت‌اند؟ چون همه جا null هست!';
    } else if (text === '/quote') {
      reply = '✨ موفقیت مجموع تلاش‌های کوچک است.';
    } else {
      reply = `✅ پیام شما دریافت شد.`;
    }

    await sendMessage(chatId, reply, { reply_markup: keyboard });
    return res.sendStatus(200);
  }

  res.sendStatus(200);
});

app.get('/', (req, res) => res.send('🤖 ربات فعال است'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 ربات روی پورت ${PORT} اجرا شد`));
