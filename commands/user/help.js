module.exports = async function help(message, sendMessage) {
  const chatId = message.chat.id;
  await sendMessage(chatId, `📖 **راهنمای کامل:**\n
  /start - شروع
  /help - راهنما
  /about - درباره
  /ping - بررسی وضعیت
  /time - ساعت و تاریخ
  /id - آیدی شما
  /profile - پروفایل
  /stats - آمار
  /joke - جوک
  /quote - نقل قول`);
};
