module.exports = async function id(message, sendMessage) {
  const chatId = message.chat.id;
  const userId = message.from.id;
  await sendMessage(chatId, `🆔 آیدی شما: ${userId}`);
};
