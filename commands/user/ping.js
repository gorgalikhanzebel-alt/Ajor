module.exports = async function ping(message, sendMessage) {
  const chatId = message.chat.id;
  await sendMessage(chatId, '🏓 پُنگ! ربات فعال است.');
};
