const fs = require('fs');
const path = require('path');

const logFile = path.join(__dirname, '../../logs.txt');

module.exports = {
  log: (message) => {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    console.log(logMessage);
    fs.appendFileSync(logFile, logMessage, { flag: 'a' });
  },
  error: (message) => {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ❌ ${message}\n`;
    console.error(logMessage);
    fs.appendFileSync(logFile, logMessage, { flag: 'a' });
  }
};
