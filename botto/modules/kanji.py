import unicodedata

import discord  # type: ignore
from discord.ext import commands  # type: ignore

import botto
from botto.modules.help import HelpCommand


class KanjiSearch(commands.Cog):
    def __init__(self, bot: botto.Botto) -> None:
        self.bot: botto.Botto = bot

    @botto.require_restricted_api()
    @botto.command(name="kanji", aliases=["k", "かんじ", "漢字"])
    async def kanji_search(self, ctx: botto.Context, kanji: str) -> None:
        """Look up a kanji character."""
        if len(kanji) > 1:
            await ctx.send("Only one kanji can be queried at a time.")
            return

        legal_prefixes = ("CJK UNIFIED IDEOGRAPH", "CJK COMPATIBILITY IDEOGRAPH")
        if not unicodedata.name(kanji, "").startswith(legal_prefixes):
            await ctx.send(
                "Kanji not found in the Japanese Industrial Standard (JIS) X kanji sets."
            )
            return

        await self.bot.send_api_event_with_context("kanji_search", ctx, kanji=kanji)

    @commands.Cog.listener()  # noqa: C901
    async def on_restricted_api_ack_kanji_search(self, payload: dict) -> None:
        channel: botto.utils.OptionalChannel = self.bot.get_channel(payload["ctx"]["channel"]["id"])
        if not channel:
            return
        message: discord.PartialMessage = channel.get_partial_message(
            payload["ctx"]["message"]["id"]
        )
        kanji = payload["kanji"]
        if not kanji:
            await message.reply(f"Kanji {payload['query_kanji']} not found in KANJIDIC2.")
            return

        embed: discord.Embed = discord.Embed(color=botto.config["MAIN_COLOR"])

        embed.set_author(name=f"Kanji Lookup - {kanji['character']}")

        embed.description = f"Stroke count: {kanji['stroke_count']}"
        if kanji["grade"]:
            embed.description += f"\nGrade: {kanji['grade']}"
        if kanji["frequency_rank"]:
            embed.description += f"\nFrequency rank: #{kanji['frequency_rank']}"
        if kanji["old_jlpt_level"]:
            embed.description += f"\nFormer JLPT level: {kanji['old_jlpt_level']}"

        lines = []
        for i, mr_object in enumerate(kanji["meanings_readings"], 1):
            if mr_object["meanings"]:
                lines.append("__" + "/".join(mr_object["meanings"]) + "__")
            else:
                lines.append("*(miscellaneous readings)*")
            if mr_object["kun_readings"]:
                lines.append("**kun:** " + "\N{IDEOGRAPHIC COMMA}".join(mr_object["kun_readings"]))
            if mr_object["on_readings"]:
                lines.append("**on:** " + "\N{IDEOGRAPHIC COMMA}".join(mr_object["on_readings"]))
            if i + 1 != len(kanji["meanings_readings"]):
                lines.append("\n")

        if kanji["meanings_readings"]:
            embed.add_field(name="Meanings and Readings", value="\n".join(lines), inline=False)

        if kanji["nanori"]:
            embed.add_field(
                name="Nanori (Pronunciation in names)",
                value="\N{IDEOGRAPHIC COMMA}".join(kanji["nanori"]),
                inline=False,
            )

        if kanji["stroke_order_gif_url"]:
            embed.set_thumbnail(url=kanji["stroke_order_gif_url"])

        await message.reply(embed=embed)

    @kanji_search.help_embed
    async def kanji_help_embed(self, help_command: HelpCommand) -> discord.Embed:
        embed: discord.Embed = discord.Embed(color=help_command.color)
        # pylint: disable=missing-format-attribute
        embed.set_author(name="{0.name} {0.signature}".format(self.kanji_search))
        # pylint: enable=missing-format-attribute
        embed.description = (
            f"{self.kanji_search.short_doc}\n\n"  # pylint: disable=no-member
            f"Kanji are the adopted logographic Chinese characters that are used in "
            f"the Japanese writing system. They are used alongside the Japanese "
            f"syllabic scripts hiragana and katakana. "
            f"The Japanese term kanji for the Chinese characters literally means "
            f'"Han characters". It is written with the same characters in the Chinese '
            f"language to refer to the character writing system, hanzi (漢字).\n\n"
            f"Tango looks through "
            f"[KANJIDIC2](http://www.edrdg.org/wiki/index.php/KANJIDIC_Project) "
            f"to provide you information on a kanji character.\n\n"
            f"Animated stroke diagrams, when available, are generated using "
            f"data from [KanjiVG](https://kanjivg.tagaini.net/) and "
            f"[maurimo's Kanimaji script](https://github.com/maurimo/kanimaji).\n\n"
            f"You can also use the Jisho command to look up more information regarding "
            f"a kanji character and its usages. To learn more, type "
            f"`{help_command.context.prefix}help jisho`."
        )
        embed.add_field(
            name="Command Aliases",
            value=" / ".join(self.kanji_search.aliases),  # pylint: disable=no-member
        )
        return embed

    @botto.require_restricted_api()
    @botto.command(aliases=["so", "ひつじゅん", "筆順", "かきじゅん", "書き順"])
    async def stroke_order(self, ctx: botto.Context, kanji: str) -> None:
        """View an animated stroke diagram of a Japanese character."""
        if len(kanji) > 1:
            await ctx.send("Only one Japanese character can be queried at a time.")
            return

        await self.bot.send_api_event_with_context("stroke_order", ctx, character=kanji)

    @commands.Cog.listener()
    async def on_restricted_api_ack_stroke_order(self, payload: dict) -> None:
        channel: botto.utils.OptionalChannel = self.bot.get_channel(payload["ctx"]["channel"]["id"])
        if not channel:
            return
        message: discord.PartialMessage = channel.get_partial_message(
            payload["ctx"]["message"]["id"]
        )
        if not payload["gif_url"]:
            await message.reply(
                f"Stroke order diagram for {payload['query_character']} was not found."
            )
        else:
            await message.reply(payload["gif_url"])

    @stroke_order.help_embed
    async def stroke_order_help_embed(self, help_command: HelpCommand) -> discord.Embed:
        embed: discord.Embed = discord.Embed(color=help_command.color)
        # pylint: disable=missing-format-attribute
        embed.set_author(name="{0.name} {0.signature}".format(self.stroke_order))
        # pylint: enable=missing-format-attribute
        embed.description = (
            f"{self.stroke_order.short_doc}\n\n"  # pylint: disable=no-member
            f"Animated stroke diagrams are generated using data from "
            f"[KanjiVG](https://kanjivg.tagaini.net/) and "
            f"[maurimo's Kanimaji script](https://github.com/maurimo/kanimaji)."
        )
        embed.add_field(
            name="Command Aliases",
            value=" / ".join(self.stroke_order.aliases),  # pylint: disable=no-member
        )
        return embed


def setup(bot: botto.Botto) -> None:
    cog = KanjiSearch(bot)
    bot.add_cog(cog)
