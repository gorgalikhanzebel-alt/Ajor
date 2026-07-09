module.exports = async function handleCallback(callbackQuery, sendMessage) {
  const data = callbackQuery.data;
  const chatId = callbackQuery.message.chat.id;

  if (data === 'btn_yes') {
    await sendMessage(chatId, '✅ شما گزینه بله را انتخاب کردید.');
  } else if (data === 'btn_no') {
    await sendMessage(chatId, '❌ شما گزینه خیر را انتخاب کردید.');
  }
};
