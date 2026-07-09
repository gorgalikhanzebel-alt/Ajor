module.exports = async function handleCallback(callbackQuery, sendMessage) {
  const data = callbackQuery.data;
  const chatId = callbackQuery.message.chat.id;

  switch (data) {
    case 'help':
      await sendMessage(chatId, '📖 راهنما');
      break;
    case 'about':
      await sendMessage(chatId, 'ℹ️ درباره ربات');
      break;
    case 'joke':
      await sendMessage(chatId, '😂 جوک');
      break;
    case 'quote':
      await sendMessage(chatId, '💪 نقل قول');
      break;
    default:
      await sendMessage(chatId, '❌ گزینه نامعتبر');
  }
};
