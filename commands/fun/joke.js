module.exports = async function joke(message, sendMessage) {
  const chatId = message.chat.id;
  const jokes = [
    'چرا برنامه‌نویس‌ها عاشق طبیعت‌اند؟ چون همه جا null هست!',
    'تفاوت برنامه‌نویس و مهندس؟ برنامه‌نویس فکر میکنه 0=1، مهندس میدونه 1=0!',
    'بهترین زبان برنامه‌نویسی؟ زبانی که رئیست بلد نیست!'
  ];
  const randomJoke = jokes[Math.floor(Math.random() * jokes.length)];
  await sendMessage(chatId, `😂 ${randomJoke}`);
};
