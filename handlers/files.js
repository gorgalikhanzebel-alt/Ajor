const File = require('../models/File');

module.exports = async function handleFile(message, sendMessage, sendPhoto, sendVideo, sendDocument) {
  const chatId = message.chat.id;
  const userId = message.from.id;
  let fileId = null;
  let fileType = null;
  let caption = message.caption || '';

  if (message.photo) {
    fileId = message.photo[message.photo.length - 1].file_id;
    fileType = 'photo';
  } else if (message.video) {
    fileId = message.video.file_id;
    fileType = 'video';
  } else if (message.document) {
    fileId = message.document.file_id;
    fileType = 'document';
  } else {
    return false;
  }

  try {
    const newFile = new File({ userId, fileId, fileType, caption });
    await newFile.save();
  } catch (error) {
    console.error('❌ خطا در ذخیره فایل:', error);
  }

  await sendMessage(chatId, `✅ فایل شما دریافت شد.\nنوع: ${fileType}\nآیدی: \`${fileId}\``, { parse_mode: 'Markdown' });
  return true;
};
