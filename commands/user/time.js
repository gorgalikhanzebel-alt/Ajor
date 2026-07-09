module.exports = async function time(message, sendMessage) {
  const chatId = message.chat.id;
  const now = new Date();
  const timeStr = now.toLocaleString('fa-IR', { timeZone: 'Asia/Tehran' });
  await sendMessage(chatId, `🕐 زمان فعلی: ${timeStr}`);
};
