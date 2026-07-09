module.exports = async function adminPanel(message, sendMessage, isAdmin) {
  const chatId = message.chat.id;

  if (!isAdmin) {
    return await sendMessage(chatId, '⚠️ شما دسترسی ادمین ندارید.');
  }

  await sendMessage(chatId, `👑 **پنل ادمین:**\n
  /ban [userId] - مسدود کردن
  /unban [userId] - رفع مسدودی
  /broadcast [پیام] - ارسال همگانی
  /stats - آمار کامل`);
};
