const User = require('../../models/User');

module.exports = async function unban(message, sendMessage) {
  const chatId = message.chat.id;
  const targetId = parseInt(message.text.split(' ')[1]);

  if (!targetId) {
    return await sendMessage(chatId, '⚠️ لطفاً آیدی کاربر را وارد کنید: /unban [userId]');
  }

  await User.findOneAndUpdate({ userId: targetId }, { isBanned: false });
  await sendMessage(chatId, `✅ کاربر ${targetId} رفع مسدودی شد.`);
};
