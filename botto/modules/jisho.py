from typing import List
from urllib.parse import quote_plus

import aiohttp
import discord
from kanaconv import KanaConv
from discord.ext import commands

import botto
from botto.modules.help import HelpCommand

romanizer = KanaConv()

# This exists because otherwise mypy will go cranky.
clean_content = commands.clean_content(fix_channel_mentions=True)


class JishoEntry:
    def __init__(self, data):
        self.is_common = data.get("is_common", None)
        self.tags = data.get("tags", [])
        self.japanese = [Japanese(jp) for jp in data.get("japanese", [])]
        self.senses = [Sense(sense) for sense in data.get("senses", [])]
        self.attribution = data.get("attribution", {})


class Japanese:
    def __init__(self, data):
        self.word = data.get("word", None)
        self.reading = data.get("reading", None)


class Sense:
    def __init__(self, data):
        self.english_definitions = data.get("english_definitions", [])
        self.parts_of_speech = data.get("parts_of_speech", [])
        self.links = [Link(link) for link in data.get("links", [])]
        self.tags = data.get("tags", [])
        self.restrictions = data.get("restrictions", [])
        self.see_also = data.get("see_also", [])
        self.antonyms = data.get("antonyms", [])
        self.source = data.get("source", [])
        self.info = data.get("info", [])


class Link:
    def __init__(self, data):
        self.text = data.get("text", None)
        self.url = data.get("url", None)


class Jisho(commands.Cog):
    def __init__(self, bot: botto.Botto) -> None:
        self.bot: botto.Botto = bot

    async def search(self, word: str) -> List[JishoEntry]:
        word = quote_plus(word)
        response = await self.bot.session.get(
            f"https://jisho.org/api/v1/search/words?keyword={word}"
        )
        entries = await response.json()
        return [JishoEntry(e) for e in entries["data"]]

    @staticmethod
    def parse_entries_into_pages(entries: List[JishoEntry]) -> List[str]:
        pages = []
        for entry in entries:
            page = []

            # Japanese and readings
            for jap in entry.japanese:
                if jap.reading:
                    romaji = romanizer.to_romaji(jap.reading)
                if jap.word and jap.reading:
                    page.append(f"**{jap.word}（{jap.reading}）** *{romaji}*")
                elif jap.reading:
                    page.append(f"**{jap.reading}** *{romaji}*")
                else:  # jap.word only
                    page.append(f"**{jap.word}**")
            if entry.is_common:
                page.append("(common word)")
            page.append("")

            # Senses (definitions)
            for i, sense in enumerate(entry.senses, 1):
                if sense.parts_of_speech:
                    parts = "(" + ", ".join(p.lower() for p in sense.parts_of_speech) + ") "
                else:
                    parts = ""
                page.append(f"{i}. {parts}{'; '.join(sense.english_definitions)}")
                for link in sense.links:
                    page.append(f"[{link.text}]({link.url})")

            pages.append("\n".join(page))
        return pages

    @botto.command(aliases=["j", "じしょ", "辞書"])
    async def jisho(self, ctx: botto.Context, *, word: clean_content):  # type: ignore
        """Look up a Japanese or English word."""
        try:
            entries = await self.search(word)
        except aiohttp.ClientResponseError:
            await ctx.reply("The dictionary is currently unavailable.")
            return
        if not entries:
            await ctx.reply(f"Could not look up {word} in the dictionary.")
            return

        pages = self.parse_entries_into_pages(entries)

        paginator = botto.utils.EmbedPaginator(ctx, entries=pages, per_page=1)
        paginator.embed.set_author(name=f"Jisho entries related to {word}")
        await paginator.paginate()

    @jisho.help_embed
    async def jisho_help_embed(self, help_command: HelpCommand) -> discord.Embed:
        embed: discord.Embed = discord.Embed(color=help_command.color)
        # pylint: disable=missing-format-attribute
        embed.set_author(name="{0.name} {0.signature}".format(self.jisho))
        # pylint: enable=missing-format-attribute
        embed.description = (
            f"{self.jisho.short_doc}\n\n"  # pylint: disable=no-member
            "botto queries entries from [Jisho](https://jisho.org/) and displays them in Discord "
            "for you and your friends.\n\n"
            "To quote their main page, Jisho is a powerful Japanese-English dictionary. It lets "
            "you find words, kanji, example sentences and more quickly and easily. Enter any "
            "Japanese text or English word and Jisho will search a myriad of data for you.\n\n"
            "Here’s a few example searches to give you a taste of what Jisho can do.\n"
            "- Great English search: `house`\n"
            "- Multi word search: `日 sunlight`\n"
            "- JLPT N3 adjectives: `#jlpt-n3 #adjective`\n"
            "- Grade 1 jōyō kanji: `#grade:1 #kanji`\n"
            "- Common words that end with 家: `#word #common ?*家`"
        )
        embed.add_field(
            name="Command Aliases",
            value=" / ".join(self.jisho.aliases),  # pylint: disable=no-member
        )
        return embed


def setup(bot: botto.Botto) -> None:
    cog = Jisho(bot)
    bot.add_cog(cog)
