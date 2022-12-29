# Multisite-Parser-Bot-for-Telegram
This repository contains a Telegram bot that is able to parse multiple websites for information and send it to the user through private messages. The websites currently supported are www.vfxmed.com, https://cgpersia.com/, and https://blendermarket.com/.

## Detailed Description
The Telegram bot is implemented using the aiogram library and is designed to be easily extensible to support additional websites. When the user sends the /start command, the bot will send them a series of private messages containing links, text, and images scraped from the supported websites.

The links and text are obtained by parsing the HTML content of the website using the lxml library. The images are downloaded and saved to the images folder, with the file name corresponding to the associated text.

In order to efficiently process and store the data obtained from the websites, the bot utilizes the json library to read and write the data to links.json and headers.json files.

#### Technologies and Libraries
- **[Python 3.x+](https://www.python.org/)**
- **[aiogram](https://docs.aiogram.dev/en/latest/)** library for creating the Telegram bot
- **[lxml](https://pypi.org/project/lxml/)** library for parsing HTML content
- **[json](https://docs.python.org/3/library/json.html#module-json)** library for reading and writing data to files
- **[requests](https://pypi.org/project/requests/)** library for making HTTP requests to websites