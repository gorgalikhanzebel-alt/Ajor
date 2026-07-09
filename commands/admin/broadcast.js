const User = require('../../models/User');

module.exports = async function broadcast(message, sendMessage) {
  const chatId = message.chat.id;
  const broadcastMessage = message.text.slice(11);

  if (!broadcastMessage) {
    return await sendMessage(chatId, '⚠️ لطفاً پیام را وارد کنید: /broadcast [پیام]');
  }

  const allUsers = await User.find({});
  let sentCount = 0;

  for (const user of allUsers) {
    try {
      await sendMessage(user.userId, `📢 **پیام همگانی:**\n${broadcastMessage}`);
      sentCount++;
    } catch (error) {
      console.error(`❌ خطا در ارسال به ${user.userId}`);
    }
  }

  await sendMessage(chatId, `✅ پیام به ${sentCount} کاربر ارسال شد.`);
};
