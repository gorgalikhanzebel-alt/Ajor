const User = require('../models/User');
const { formatDate } = require('../utils/helpers');
const logger = require('../utils/logger');

// --- مدیریت اصلی دکمه‌ها ---
module.exports = async function handleCallback(callbackQuery, sendMessage, sendPhoto, sendVideo, sendDocument) {
  const data = callbackQuery.data;
  const chatId = callbackQuery.message.chat.id;
  const messageId = callbackQuery.message.message_id;
  const userId = callbackQuery.from.id;

  // ثبت لاگ
  logger.log(`🔘 کلیک دکمه از ${userId}: ${data}`);

  try {
    // دریافت اطلاعات کاربر
    const user = await User.findOne({ userId });
    const isAdmin = user && user.isAdmin;

    // تقسیم داده دکمه (برای دکمه‌های پویا)
    const [action, param] = data.split('|');

    switch (action) {
      // --- منوی اصلی ---
      case 'main_menu':
        await showMainMenu(chatId, messageId, sendMessage);
        break;

      // --- دکمه‌های راهنما و درباره ---
      case 'help':
        await sendMessage(chatId, `📖 **راهنمای کامل:**\n
        /start - شروع
        /help - راهنما
        /about - درباره
        /ping - بررسی وضعیت
        /time - ساعت و تاریخ
        /id - آیدی شما
        /profile - پروفایل
        /stats - آمار
        /joke - جوک
        /quote - نقل قول`);
        break;

      case 'about':
        await sendMessage(chatId, '🤖 **ربات فوق‌العاده**\nنسخه 4.0\nNode.js + MongoDB\nتوسعه‌دهنده: @gorgalikhanzebel');
        break;

      // --- دکمه‌های سرگرمی ---
      case 'joke':
        const jokes = [
          'چرا برنامه‌نویس‌ها عاشق طبیعت‌اند؟ چون همه جا null هست!',
          'تفاوت برنامه‌نویس و مهندس؟ برنامه‌نویس فکر میکنه 0=1، مهندس میدونه 1=0!',
          'بهترین زبان برنامه‌نویسی؟ زبانی که رئیست بلد نیست!'
        ];
        const randomJoke = jokes[Math.floor(Math.random() * jokes.length)];
        await sendMessage(chatId, `😂 ${randomJoke}`);
        break;

      case 'quote':
        const quotes = [
          '✨ موفقیت مجموع تلاش‌های کوچک روزانه است.',
          '💪 تنها راه انجام کار عالی، انجام کاری است که دوست داری.',
          '🌟 آینده متعلق به کسانی است که به رویاهای خود ایمان دارند.'
        ];
        const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
        await sendMessage(chatId, randomQuote);
        break;

      // --- پروفایل و آیدی ---
      case 'profile':
        if (user) {
          const profileText = `👤 **پروفایل شما:**\n
          آیدی: ${user.userId}
          نام کاربری: @${user.username || 'ندارد'}
          نام: ${user.firstName || 'ندارد'}
          تعداد پیام‌ها: ${user.messagesCount}
          تاریخ ثبت‌نام: ${formatDate(user.registeredAt)}`;
          await sendMessage(chatId, profileText);
        } else {
          await sendMessage(chatId, '⚠️ کاربر یافت نشد.');
        }
        break;

      case 'id':
        await sendMessage(chatId, `🆔 آیدی شما: ${userId}`);
        break;

      // --- دکمه‌های ادمین ---
      case 'admin_panel':
        if (!isAdmin) {
          await sendMessage(chatId, '⚠️ شما دسترسی ادمین ندارید.');
          break;
        }
        await sendMessage(chatId, `👑 **پنل ادمین:**\n
        /ban [userId] - مسدود کردن
        /unban [userId] - رفع مسدودی
        /broadcast [پیام] - ارسال همگانی
        /stats - آمار کامل`);
        break;

      case 'admin_stats':
        if (!isAdmin) {
          await sendMessage(chatId, '⚠️ شما دسترسی ادمین ندارید.');
          break;
        }
        // اینجا می‌تونی آمار رو نمایش بدی
        await sendMessage(chatId, '📊 **آمار ربات در حال توسعه...**');
        break;

      // --- دکمه‌های تایید/انصراف ---
      case 'confirm':
        if (param === 'yes') {
          await sendMessage(chatId, '✅ عملیات با موفقیت انجام شد.');
        } else if (param === 'no') {
          await sendMessage(chatId, '❌ عملیات لغو شد.');
        }
        break;

      // --- دکمه‌های صفحه‌بندی ---
      case 'page':
        const page = parseInt(param) || 1;
        // اینجا می‌تونی لیست صفحه‌بندی شده رو نمایش بدی
        await sendMessage(chatId, `📄 صفحه ${page} از ۱۰`);
        break;

      // --- دکمه‌های لینک ---
      case 'link':
        if (param === 'github') {
          await sendMessage(chatId, '🔗 [گیت‌هاب پروژه](https://github.com/gorgalikhanzebel-alt/Ajor)');
        } else if (param === 'telegram') {
          await sendMessage(chatId, '🔗 [کانال تلگرام](https://t.me/Ajorpareh)');
        }
        break;

      // --- دکمه حذف پیام ---
      case 'delete':
        try {
          const url = `https://api.telegram.org/bot${process.env.BOT_TOKEN}/deleteMessage`;
          await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: chatId, message_id: messageId })
          });
        } catch (error) {
          console.error('❌ خطا در حذف پیام:', error);
        }
        break;

      // --- منوی کاربری (Custom) ---
      case 'user_menu':
        await showUserMenu(chatId, messageId, sendMessage);
        break;

      // --- دکمه پیش‌فرض (برای داده‌های ناشناخته) ---
      default:
        await sendMessage(chatId, '❌ گزینه نامعتبر یا منقضی شده.');
    }

    // پاسخ به تلگرام برای جلوگیری از خطای "callback_query timeout"
    await answerCallbackQuery(callbackQuery.id);

  } catch (error) {
    console.error('❌ خطا در پردازش دکمه:', error);
    await sendMessage(chatId, '❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.');
  }
};

// --- نمایش منوی اصلی (با دکمه‌های بیشتر) ---
async function showMainMenu(chatId, messageId, sendMessage) {
  const keyboard = {
    inline_keyboard: [
      [
        { text: '📖 راهنما', callback_data: 'help' },
        { text: 'ℹ️ درباره', callback_data: 'about' }
      ],
      [
        { text: '😂 جوک', callback_data: 'joke' },
        { text: '💪 نقل قول', callback_data: 'quote' }
      ],
      [
        { text: '👤 پروفایل', callback_data: 'profile' },
        { text: '🆔 آیدی من', callback_data: 'id' }
      ],
      [
        { text: '👑 پنل ادمین', callback_data: 'admin_panel' },
        { text: '🔗 لینک‌ها', callback_data: 'link_menu' }
      ]
    ]
  };

  // ویرایش پیام قبلی (به جای ارسال پیام جدید)
  try {
    const url = `https://api.telegram.org/bot${process.env.BOT_TOKEN}/editMessageText`;
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        message_id: messageId,
        text: '📋 **منوی اصلی ربات:**\nیکی از گزینه‌های زیر را انتخاب کنید.',
        reply_markup: keyboard,
        parse_mode: 'Markdown'
      })
    });
  } catch (error) {
    console.error('❌ خطا در ویرایش پیام:', error);
    // اگر ویرایش ممکن نبود، پیام جدید بفرست
    await sendMessage(chatId, '📋 **منوی اصلی ربات:**\nیکی از گزینه‌های زیر را انتخاب کنید.', {
      reply_markup: keyboard
    });
  }
}

// --- نمایش منوی کاربری ---
async function showUserMenu(chatId, messageId, sendMessage) {
  const keyboard = {
    inline_keyboard: [
      [
        { text: '📊 آمار من', callback_data: 'user_stats' },
        { text: '📁 فایل‌های من', callback_data: 'user_files' }
      ],
      [
        { text: '🔙 بازگشت به منوی اصلی', callback_data: 'main_menu' }
      ]
    ]
  };

  try {
    const url = `https://api.telegram.org/bot${process.env.BOT_TOKEN}/editMessageText`;
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        message_id: messageId,
        text: '👤 **منوی کاربری:**\nلطفاً یکی از گزینه‌ها را انتخاب کنید.',
        reply_markup: keyboard,
        parse_mode: 'Markdown'
      })
    });
  } catch (error) {
    await sendMessage(chatId, '👤 **منوی کاربری:**', { reply_markup: keyboard });
  }
}

// --- پاسخ به درخواست callback_query (برای جلوگیری از خطا) ---
async function answerCallbackQuery(callbackQueryId) {
  try {
    const url = `https://api.telegram.org/bot${process.env.BOT_TOKEN}/answerCallbackQuery`;
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        callback_query_id: callbackQueryId,
        text: '✅', // پیام کوتاه که به کاربر نشان داده میشه
        show_alert: false // اگر true باشه، به صورت پیام هشدار نمایش داده میشه
      })
    });
  } catch (error) {
    console.error('❌ خطا در پاسخ به callback:', error);
  }
}

// --- اضافه کردن دکمه‌های جدید به راحتی ---
// برای اضافه کردن دکمه جدید، فقط کافیه یک case جدید به switch اضافه کنی
// و تابع مربوطه رو بنویسی.
