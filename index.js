const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

const config = require('./config/settings');
const { connectDB } = require('./services/database');
const { sendMessage, sendPhoto, sendVideo, sendDocument } = require('./services/telegram');
const handleCommand = require('./handlers/commands');
const handleFile = require('./handlers/files');
const handleCallback = require('./handlers/callback');
const handleInline = require('./handlers/inline');
const authMiddleware = require('./middlewares/auth');
const loggingMiddleware = require('./middlewares/logging');
const { registerUser } = require('./utils/helpers');

connectDB();
app.use(loggingMiddleware);

app.post('/webhook', authMiddleware, async (req, res) => {
  const { message, callback_query, inline_query } = req.body;

  if (message) {
    await registerUser(message);
    if (message.text && message.text.startsWith('/')) {
      await handleCommand(message, sendMessage, sendPhoto, sendVideo, sendDocument);
    } else if (message.photo || message.video || message.document) {
      await handleFile(message, sendMessage, sendPhoto, sendVideo, sendDocument);
    } else if (message.text) {
      await sendMessage(message.chat.id, `✅ پیام شما دریافت شد.`);
    }
  } else if (callback_query) {
    await handleCallback(callback_query, sendMessage);
  } else if (inline_query) {
    await handleInline(inline_query);
  }
  res.sendStatus(200);
});

app.get('/', (req, res) => res.send('🤖 ربات فوق‌العاده فعال است!'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 ربات روی پورت ${PORT} در حال اجراست`));
