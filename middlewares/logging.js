const logger = require('../utils/logger');

module.exports = function loggingMiddleware(req, res, next) {
  const { message } = req.body;
  if (message) {
    logger.log(`📩 پیام از ${message.from.id}: ${message.text || 'فایل'}`);
  }
  next();
};
