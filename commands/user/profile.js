const User = require('../../models/User');
const { formatDate } = require('../../utils/helpers');

module.exports = async function profile(message, sendMessage) {
  const chatId = message.chat.id;
  const userId = message.from.id;
  const user = await User.findOne({ userId });

  if (user) {
    const text = `👤 **پروفایل شما:**\n
    آیدی: ${user.userId}
    نام کاربری: @${user.username || 'ندارد'}
    نام: ${user.firstName || 'ندارد'}
    تعداد پیام‌ها: ${user.messagesCount}
    تاریخ ثبت‌نام: ${formatDate(user.registeredAt)}`;
    await sendMessage(chatId, text);
  } else {
    await sendMessage(chatId, '⚠️ کاربر یافت نشد.');
  }
};
