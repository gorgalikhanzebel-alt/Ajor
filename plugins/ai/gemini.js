const axios = require('axios');
const config = require('../../config/settings');

module.exports = async function askGemini(prompt) {
  try {
    const response = await axios.post(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${config.aiApiKey}`,
      {
        contents: [{ parts: [{ text: prompt }] }]
      }
    );
    return response.data.candidates[0].content.parts[0].text;
  } catch (error) {
    console.error('❌ خطا در تماس با Gemini:', error);
    return '❌ خطا در پردازش درخواست.';
  }
};
