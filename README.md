# Tango!

![Python][python-shield]
[![discord.py][discordpy-shield]][discordpy-url]
[![License][license-shield]][license-url]
[![Issues][issues-shield]][issues-url]
[![Commits][commits-shield]][commits-url]
[![Discord][discord-shield]][discord-url]

[python-shield]: https://img.shields.io/badge/python-3.7%20%7C%203.8-blue.svg
[discordpy-shield]: https://img.shields.io/badge/discord.py-1.6.0-g
[discordpy-url]: https://github.com/Rapptz/discord.py/tree/v1.6.0
[license-shield]: https://img.shields.io/github/license/MusicOnline/Tango-Bot
[license-url]: https://github.com/MusicOnline/Tango-Bot/blob/master/LICENSE
[issues-shield]: https://img.shields.io/github/issues/MusicOnline/Tango-Bot
[issues-url]: https://github.com/MusicOnline/Tango-Bot/issues
[commits-shield]: https://img.shields.io/github/commit-activity/m/MusicOnline/Tango-Bot
[commits-url]: https://github.com/MusicOnline/Tango-Bot/commits
[discord-shield]: https://img.shields.io/discord/470114854762577920?color=%237289DA&label=chat%2Fsupport&logo=discord&logoColor=white
[discord-url]: https://discord.gg/wp7Wxzs

Tango is a simplistic bot here to help you learn and have fun with Japanese!

Look up words, view animated stroke diagrams and play Shiritori (Japanese word chain)!

Tango's help command is very informative regarding topics related to the commands you are using! Be sure to read them to explore more Japanese stuff and Tango!

This is the Discord bot (frontend) component of Tango.
The web and backend component is [Tango-Web][tango-web-url].

[tango-web-url]: https://github.com/MusicOnline/Tango-Web

## User's Information

### Prefix

Call upon Tango using any of the prefixes: `@Tango`, `tango`, `tg` or `t` (each of them followed by space) and the command name!

Tango also has Japanese prefixes and most commands have Japanese aliases. You can use the prefix たんご or タンゴ (optional space afterwards) if you're into that! The command aliases can be seen on each command's help page.

### Commands

Currently, the main commands include:

-   help | ヘルプ
-   jisho | j | じしょ | 辞書
-   kanji | k | かんじ | 漢字
-   strokeorder | so | ひつじゅん | 筆順 | かきじゅん | 書き順
-   shiritori | しりとり | 尻取り
-   shiritori check | かくにん | 確認

### Regarding the name

Tango is a play on the differences between pronouncing English and Japanese (romaji). In English, it would be tango as in _tango orange_, the color! In Japanese, たんご or タンゴ is pronounced something like _tahn-goh_. It also happens to be the reading of 単語, which means 'word' or 'vocabulary'!

## Developer's Information

### Requirements

-   Python 3.7 and above
-   [Tango-Web][tango-web-url]

### Installation

Please refer to [Botto][botto-url]'s installation instructions.<br>
You will also need to install Tango Web to run this bot.

[botto-url]: https://github.com/MusicOnline/Botto

### Usage

Please refer to [Botto][botto-url]'s usage instructions.<br>
Tango Bot requires Tango Web to be running to function properly.

### Development

Tango was created as I was learning Japanese. Sure, I did learn new Japanese stuff while building Tango. However, scraping big data like JMdict and KANJIDIC2 was a great learning experience too. Feel free to make a PR or issue to improve the bot.

I don't have any specific objectives with Tango ever since I learned of similar bots. However, I do intend to add simple Japanese localization to make more of a learning environment. That might not happen anytime soon though.

For further discussion, feel free to join the [support server](https://discord.gg/wp7Wxzs).

## Contributing

Contributions are always welcome. You may also open issues and feature requests on the issue tracker.<br>
Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for further details.
