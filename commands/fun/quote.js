module.exports = async function quote(message, sendMessage) {
  const chatId = message.chat.id;
  const quotes = [
    '✨ موفقیت مجموع تلاش‌های کوچک روزانه است.',
    '💪 تنها راه انجام کار عالی، انجام کاری است که دوست داری.',
    '🌟 آینده متعلق به کسانی است که به رویاهای خود ایمان دارند.'
  ];
  const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
  await sendMessage(chatId, randomQuote);
};
