module.exports = async function start(message, sendMessage) {
  const chatId = message.chat.id;
  const firstName = message.from.first_name || 'کاربر';
  await sendMessage(chatId, `👋 سلام ${firstName}!\nبه ربات فوق‌العاده خوش آمدید.\nلیست دستورات: /help`);
};
