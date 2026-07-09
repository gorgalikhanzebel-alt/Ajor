const config = require('../config/settings');
const fetch = require('node-fetch');

const botToken = config.botToken;

async function sendMessage(chatId, text, options = {}) {
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text, ...options })
    });
    return await response.json();
  } catch (error) {
    console.error('❌ خطا در ارسال پیام:', error);
  }
}

async function sendPhoto(chatId, fileId, caption = '') {
  const url = `https://api.telegram.org/bot${botToken}/sendPhoto`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, photo: fileId, caption })
    });
    return await response.json();
  } catch (error) {
    console.error('❌ خطا در ارسال عکس:', error);
  }
}

async function sendVideo(chatId, fileId, caption = '') {
  const url = `https://api.telegram.org/bot${botToken}/sendVideo`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, video: fileId, caption })
    });
    return await response.json();
  } catch (error) {
    console.error('❌ خطا در ارسال فیلم:', error);
  }
}

async function sendDocument(chatId, fileId, caption = '') {
  const url = `https://api.telegram.org/bot${botToken}/sendDocument`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, document: fileId, caption })
    });
    return await response.json();
  } catch (error) {
    console.error('❌ خطا در ارسال فایل:', error);
  }
}

module.exports = { sendMessage, sendPhoto, sendVideo, sendDocument };
