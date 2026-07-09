const User = require('../../models/User');
const { formatDate } = require('../../utils/helpers');
const logger = require('../../utils/logger');

module.exports = async function start(message, sendMessage) {
  const chatId = message.chat.id;
  const userId = message.from.id;
  const firstName = message.from.first_name || 'کاربر';
  const username = message.from.username || '';
  const lastName = message.from.last_name || '';

  try {
    // --- بررسی وجود کاربر در دیتابیس ---
    let user = await User.findOne({ userId });
    let isNewUser = false;

    if (!user) {
      // ثبت کاربر جدید
      user = new User({
        userId,
        username,
        firstName,
        lastName,
        registeredAt: new Date(),
        lastActive: new Date(),
        messagesCount: 1
      });
      await user.save();
      isNewUser = true;
      logger.log(`🆕 کاربر جدید ثبت شد: ${userId} (${firstName})`);
    } else {
      // به‌روزرسانی کاربر موجود
      user.lastActive = new Date();
      user.messagesCount += 1;
      await user.save();
    }

    // --- ساخت پیام خوش‌آمدگویی شخصی‌سازی شده ---
    let welcomeMessage = '';
    
    if (isNewUser) {
      welcomeMessage = `🎉 **به ربات فوق‌العاده خوش آمدید، ${firstName}!**\n\n` +
                       `🌟 این ربات با امکانات پیشرفته ساخته شده تا همه نیازهای شما رو برآورده کنه.\n` +
                       `📋 برای شروع، از دکمه‌های زیر استفاده کنید یا دستور /help را بفرستید.\n\n` +
                       `👤 **شناسه شما:** ${userId}\n` +
                       `📅 **تاریخ ثبت‌نام:** ${formatDate(new Date())}`;
    } else {
      const lastActive = user.lastActive ? formatDate(user.lastActive) : 'نامشخص';
      welcomeMessage = `👋 **خوش برگشتی، ${firstName}!**\n\n` +
                       `📊 **آمار شما:**\n` +
                       `• تعداد پیام‌ها: ${user.messagesCount}\n` +
                       `• آخرین فعالیت: ${lastActive}\n\n` +
                       `📋 از دکمه‌های زیر برای دسترسی سریع استفاده کنید.`;
    }

    // --- ساخت منوی اصلی با دکمه‌های شیشه‌ای کامل ---
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
        ],
        [
          { text: '📁 فایل‌های من', callback_data: 'user_files' },
          { text: '📊 آمار من', callback_data: 'user_stats' }
        ]
      ]
    };

    // --- ارسال پیام خوش‌آمدگویی با دکمه‌ها ---
    await sendMessage(chatId, welcomeMessage, {
      parse_mode: 'Markdown',
      reply_markup: keyboard
    });

    // --- اضافه کردن منوی شناور (اختیاری) ---
    // این منو همیشه پایین صفحه نمایش داده میشه
    const floatingKeyboard = {
      keyboard: [
        ['📖 راهنما', 'ℹ️ درباره'],
        ['😂 جوک', '💪 نقل قول'],
        ['👤 پروفایل', '🆔 آیدی من']
      ],
      resize_keyboard: true,
      one_time_keyboard: false
    };

    // برای منوی شناور، می‌تونی یک پیام جداگانه بفرستی یا از همین پیام استفاده کنی
    // اما بهتره که فقط یک بار ارسال بشه تا شلوغ نشه.
    // اگه می‌خوای منوی شناور هم داشته باشی، می‌تونی این خط رو فعال کنی:
    // await sendMessage(chatId, '📱 منوی شناور فعال شد.', { reply_markup: floatingKeyboard });

  } catch (error) {
    console.error('❌ خطا در اجرای دستور start:', error);
    // پیام ساده در صورت خطا
    await sendMessage(chatId, `👋 سلام ${firstName}!\nبه ربات خوش آمدید.\nاز /help برای راهنما استفاده کنید.`);
  }
};
