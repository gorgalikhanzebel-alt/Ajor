const User = require('../../models/User');

module.exports = async function ban(message, sendMessage) {
  const chatId = message.chat.id;
  const targetId = parseInt(message.text.split(' ')[1]);

  if (!targetId) {
    return await sendMessage(chatId, '⚠️ لطفاً آیدی کاربر را وارد کنید: /ban [userId]');
  }

  await User.findOneAndUpdate({ userId: targetId }, { isBanned: true });
  await sendMessage(chatId, `✅ کاربر ${targetId} مسدود شد.`);
};
