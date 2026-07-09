module.exports = async function about(message, sendMessage) {
  const chatId = message.chat.id;
  await sendMessage(chatId, `🤖 **ربات فوق‌العاده**\nنسخه 4.0\nNode.js + MongoDB\nتوسعه‌دهنده: @gorgalikhanzebel`);
};
