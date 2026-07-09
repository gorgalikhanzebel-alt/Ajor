const config = require('../config/settings');
const fetch = require('node-fetch');

const botToken = config.botToken;
const MAX_MESSAGE_LENGTH = 4096; // محدودیت تلگرام

// --- تابع اصلی ارسال پیام (پیشرفته) ---
async function sendMessage(chatId, text, options = {}) {
  // اگر پیام طولانی‌تر از حد مجاز بود، چند تکه کن
  if (text && text.length > MAX_MESSAGE_LENGTH) {
    const parts = splitMessage(text, MAX_MESSAGE_LENGTH);
    for (const part of parts) {
      await sendSingleMessage(chatId, part, options);
    }
    return;
  }

  return await sendSingleMessage(chatId, text, options);
}

// --- تابع ارسال یک پیام (با مدیریت خطا و تلاش مجدد) ---
async function sendSingleMessage(chatId, text, options, retries = 3) {
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  
  // تنظیمات پیش‌فرض
  const defaultOptions = {
    parse_mode: 'Markdown', // می‌تونی به 'HTML' هم تغییر بدی
    disable_web_page_preview: false,
    ...options
  };

  // حذف options اضافی که ممکنه تداخل ایجاد کنن
  if (defaultOptions.reply_markup) {
    defaultOptions.reply_markup = JSON.stringify(defaultOptions.reply_markup);
  }

  const payload = {
    chat_id: chatId,
    text: text,
    ...defaultOptions
  };

  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      
      if (result.ok) {
        console.log(`✅ پیام ارسال شد به ${chatId}`);
        return result;
      } else {
        console.error(`❌ خطا در ارسال پیام (تلاش ${attempt + 1}):`, result.description);
        if (attempt === retries - 1) {
          console.error('❌ همه تلاش‌ها ناموفق بود.');
          return result;
        }
        // منتظر بمان و دوباره تلاش کن
        await new Promise(resolve => setTimeout(resolve, 2000 * (attempt + 1)));
      }
    } catch (error) {
      console.error(`❌ خطای شبکه (تلاش ${attempt + 1}):`, error);
      if (attempt === retries - 1) {
        console.error('❌ همه تلاش‌ها ناموفق بود.');
      }
      await new Promise(resolve => setTimeout(resolve, 2000 * (attempt + 1)));
    }
  }
}

// --- تابع کمکی برای تقسیم پیام طولانی ---
function splitMessage(text, maxLength) {
  const parts = [];
  while (text.length > maxLength) {
    let splitIndex = text.lastIndexOf('\n', maxLength);
    if (splitIndex === -1) splitIndex = text.lastIndexOf(' ', maxLength);
    if (splitIndex === -1) splitIndex = maxLength;
    
    parts.push(text.substring(0, splitIndex));
    text = text.substring(splitIndex).trim();
  }
  if (text) parts.push(text);
  return parts;
}

// --- تابع ارسال عکس (با پشتیبانی از دکمه) ---
async function sendPhoto(chatId, fileId, caption = '', options = {}) {
  const url = `https://api.telegram.org/bot${botToken}/sendPhoto`;
  try {
    const payload = {
      chat_id: chatId,
      photo: fileId,
      caption: caption,
      ...options
    };

    if (payload.reply_markup) {
      payload.reply_markup = JSON.stringify(payload.reply_markup);
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!result.ok) console.error('❌ خطا در ارسال عکس:', result.description);
    return result;
  } catch (error) {
    console.error('❌ خطا در ارسال عکس:', error);
  }
}

// --- تابع ارسال فیلم (با پشتیبانی از دکمه) ---
async function sendVideo(chatId, fileId, caption = '', options = {}) {
  const url = `https://api.telegram.org/bot${botToken}/sendVideo`;
  try {
    const payload = {
      chat_id: chatId,
      video: fileId,
      caption: caption,
      ...options
    };

    if (payload.reply_markup) {
      payload.reply_markup = JSON.stringify(payload.reply_markup);
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!result.ok) console.error('❌ خطا در ارسال فیلم:', result.description);
    return result;
  } catch (error) {
    console.error('❌ خطا در ارسال فیلم:', error);
  }
}

// --- تابع ارسال فایل (با پشتیبانی از دکمه) ---
async function sendDocument(chatId, fileId, caption = '', options = {}) {
  const url = `https://api.telegram.org/bot${botToken}/sendDocument`;
  try {
    const payload = {
      chat_id: chatId,
      document: fileId,
      caption: caption,
      ...options
    };

    if (payload.reply_markup) {
      payload.reply_markup = JSON.stringify(payload.reply_markup);
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!result.ok) console.error('❌ خطا در ارسال فایل:', result.description);
    return result;
  } catch (error) {
    console.error('❌ خطا در ارسال فایل:', error);
  }
}

module.exports = { sendMessage, sendPhoto, sendVideo, sendDocument };
