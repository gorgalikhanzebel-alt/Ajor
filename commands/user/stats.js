const User = require('../../models/User');
const Message = require('../../models/Message');
const File = require('../../models/File');

module.exports = async function stats(message, sendMessage, isAdmin) {
  const chatId = message.chat.id;

  if (!isAdmin) {
    return await sendMessage(chatId, '⚠️ این دستور فقط برای ادمین است.');
  }

  const totalUsers = await User.countDocuments();
  const totalMessages = await Message.countDocuments();
  const totalFiles = await File.countDocuments();

  await sendMessage(chatId, `📊 **آمار ربات:**\n
  👥 کاربران: ${totalUsers}
  💬 پیام‌ها: ${totalMessages}
  📁 فایل‌ها: ${totalFiles}
  🚀 وضعیت: آنلاین`);
};
