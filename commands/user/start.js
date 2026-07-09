module.exports = async function start(message, sendMessage) {
  const chatId = message.chat.id;
  const firstName = message.from.first_name || 'کاربر';

  // ساخت دکمه‌های شیشه‌ای
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
      ]
    ]
  };

  await sendMessage(chatId, `👋 سلام ${firstName}!\nبه ربات فوق‌العاده خوش آمدید.\nاز دکمه‌های زیر استفاده کن یا دستورات رو با /help ببین.`, {
    reply_markup: JSON.stringify(keyboard)
  });
};
