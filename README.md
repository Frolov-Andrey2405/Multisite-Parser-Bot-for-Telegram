# Multisite-Parser-Bot-for-Telegram
This repository contains a Telegram bot that was created using the aiogram library. The bot retrieves data from a MySQL database and publishes it in a Telegram channel.

## Detailed Description
The Telegram bot in this repository was created using the aiogram library and is designed to be easily extendable for support and development. The purpose of the bot is to automate the process of publishing new addons and elements of add-ons in a Telegram channel. These publications consist of messages containing links, text, and images taken from the data stored in the MySQL database.

New data is entered into the database asynchronously using the aiomysql library and .json files. This data is then sorted and checked for similarity in order to link the Vfxmed and BlenderMarket tables. 

Parsing occurs on the following websites: 
- https://blendermarket.com/products
- https://www.vfxmed.com/tag/blender/page/

Asynchronous parsing (using asyncio, httpx, and Semaphore technologies) is performed by parsing the HTML content of the sites using json, re, BeautifulSoup, requests, and lxml. 

The structure of the data parsed from vfxmed.com has the following format:

`{
"link": href,
"title": title,
"download_link": download_link
}`

The structure of the data parsed from blendermarket.com has the following format:

`{
'off_link': link,
'name_of_tools': name_of_tools,
'url_on_image': url_on_image,
}`


#### Technologies and Libraries
- **[Python 3.x+](https://www.python.org/)**: served a central role as the main programming language in the project
- **[aiogram](https://aiogram.readthedocs.io/en/latest/)**: a library for creating Telegram bots in Python
- **[MySQL](https://dev.mysql.com/doc/)**: a popular database management system
- **[aiomysql](https://aiomysql.readthedocs.io/en/latest/)**: a library for accessing MySQL databases asynchronously in Python
- **[json](https://docs.python.org/3/library/json.html)**: a data interchange format that is used for storing and exchanging data
- **[re](https://docs.python.org/3/library/re.html)**(regular expressions): a library in Python for searching and manipulating strings
- **[BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/)**: a library for parsing HTML and XML in Python
- **[requests](https://requests.readthedocs.io/en/latest/)**: a library for making HTTP requests in Python
- **[lxml](https://lxml.de/)**: a library for parsing XML and HTML in Python
- **[asyncio](https://docs.python.org/3/library/asyncio.html)**: a library for asynchronous programming in Python
- **[httpx](https://www.python-httpx.org/)**: an asynchronous HTTP library for Python
- **[Semaphore](https://docs.python.org/3/library/asyncio-semaphore.html)**: a library for controlling access to resources in Python