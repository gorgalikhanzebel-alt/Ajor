const config = require('./config/settings');
const { connectDB } = require('./services/database');
const { sendMessage } = require('./services/telegram');
const handleCommand = require('./handlers/commands');
