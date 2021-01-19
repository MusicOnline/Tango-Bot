import asyncio
from typing import Any, Dict, Optional

import discord  # type: ignore
from discord.ext import commands  # type: ignore

import botto
from botto.modules.help import HelpCommand


class Shiritori(commands.Cog):
    def __init__(self, bot: botto.Botto) -> None:
        self.bot: botto.Botto = bot

    @botto.require_restricted_api()
    @botto.group(aliases=["しりとり", "尻取り"], invoke_without_command=True)
    async def shiritori(self, ctx: botto.Context, time_limit: int = 20) -> None:
        """Play Shiritori with Tango!"""
        if not 5 <= time_limit <= 60:
            await ctx.reply("Time limit must be between 5 - 60 seconds.")
            return

        embed: discord.Embed = discord.Embed(color=botto.config["MAIN_COLOR"])
        embed.set_author(name="A game of Shiritori is starting!")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.description = (
            "The rules for my game are as follows:\n"
            "1. Words must be written in hiragana or katakana accordingly.\n"
            "2. Words must consist of at least two syllables/kana. (Final sokuon/dash is ignored)\n"
            "3. Words must be nouns only.\n"
            "4. A word must not be repeated twice.\n"
            f"5. The time limit for each turn is {time_limit} seconds.\n\n"
            "All messages following this will be considered as answers. If you want the bot to "
            "ignore a message (like if you're replying to a friend in the same channel), add a "
            "backslash (`\\`) before your message.\n\n"
            "Get ready, the game will start in 5 seconds!"
        )
        await ctx.reply(embed=embed)
        await asyncio.sleep(5)

        await ctx.reply(f"{ctx.author.mention} Starting off, しりとり!")

        await self.wait_for_and_query_next_word(ctx, time_limit)

    async def wait_for_and_query_next_word(self, ctx: botto.Context, timeout: int) -> None:
        def check(message: discord.Message) -> bool:
            return (
                ctx.author == message.author
                and ctx.channel == message.channel
                and message.content is not None
                and not message.content.startswith("\\")
            )

        word: Optional[str]
        try:
            msg: discord.Message = await self.bot.wait_for("message", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            word = None
        else:
            word = msg.content.replace(" ", "").replace("\N{IDEOGRAPHIC SPACE}", "")
            ctx = await self.bot.get_context(msg, cls=botto.Context)
        await self.bot.send_api_event_with_context("shiritori", ctx, word=word, timeout=timeout)

    @commands.Cog.listener()
    async def on_restricted_api_ack_shiritori(self, payload: Dict[str, Any]) -> None:
        channel: botto.utils.OptionalChannel = self.bot.get_channel(payload["ctx"]["channel"]["id"])
        try:
            message: discord.Message = discord.utils.get(
                self.bot.cached_messages, id=payload["ctx"]["message"]["id"]
            ) or await channel.fetch_message(  # type: ignore
                payload["ctx"]["message"]["id"]
            )
        except (AttributeError, discord.NotFound):
            payload["end_type"] = "silent"
        else:
            ctx: botto.Context = await self.bot.get_context(message, cls=botto.Context)

        if not payload["end_type"]:
            reading: str = payload["next_word"]["reading"]
            writing: Optional[str] = payload["next_word"]["writing"]
            response: str
            if writing:
                response = f"{reading} ({writing})"
            else:
                response = reading
            await ctx.reply(response)
            await self.wait_for_and_query_next_word(ctx, payload["timeout"])
            return
        if payload["end_type"] == "silent":
            return

        end_messages: Dict[str, str] = {
            "timeout": "Time's up!",
            "repeat": "You repeated that word!",
            "bad_word": "That did not seem like proper Japanese with kana only.",
            "bad_continuation": (
                "The first syllable of that word did not match "
                "the last syllable of the previous word."
            ),
            "not_noun": "That is not a common noun!",
            "n_ending": "Words that end with ん or ン end the game.",
            "win_no_more_words": "Miraculously, you have beaten the CPU player!",
        }
        await ctx.reply(end_messages[payload["end_type"]] + f" (Score: {payload['score']})")

    @shiritori.help_embed
    async def shiritori_help_embed(self, help_command: HelpCommand) -> discord.Embed:
        embed: discord.Embed = discord.Embed(color=help_command.color)
        # pylint: disable=missing-format-attribute
        embed.set_author(name="{0.name} {0.signature}".format(self.shiritori))
        # pylint: enable=missing-format-attribute
        embed.description = (
            f"{self.shiritori.short_doc}\n\n"  # pylint: disable=no-member
            "Shiritori (しりとり) is a Japanese word game in which the players are required to say a "
            "word which begins with the final kana of the previous word.\n\n"
            '"Shiritori" literally means "taking the end" or "taking the rear".\n'
            "The most similar game in English is Word Chain.\n"
            "[Read more on Wikipedia.](https://en.wikipedia.org/wiki/Shiritori)"
        )
        embed.add_field(
            name="Command Aliases",
            value=" / ".join(self.shiritori.aliases),  # pylint: disable=no-member
        )
        embed.add_field(
            name="Checking Your Words",
            value=(
                "Tango provides you with an easy way to check if your word is valid without "
                f"starting a game. To learn more, type `{help_command.context.prefix} help "
                "shiritori check`."
            ),
        )
        embed.add_field(
            name="Wordbase",
            value=(
                "Tango's wordbase is built with data from the "
                "[JMdict](https://www.edrdg.org/jmdict/j_jmdict.html) project. "
            ),
        )
        embed.set_image(url="http://www.619.io/assets/img/shiritori/shiritori.png")
        return embed

    @botto.require_restricted_api()
    @shiritori.command(name="check", aliases=["かくにん", "確認"])
    async def shiritori_check(self, ctx: botto.Context, word: str) -> None:
        """Check if your word is Shiritori-compliant."""
        await self.bot.send_api_event_with_context("shiritori_check", ctx, word=word)

    @commands.Cog.listener()
    async def on_restricted_api_ack_shiritori_check(self, payload: Dict[str, Any]) -> None:
        channel: botto.utils.OptionalChannel = self.bot.get_channel(payload["ctx"]["channel"]["id"])
        if not channel:
            return
        message: discord.PartialMessage = channel.get_partial_message(
            payload["ctx"]["message"]["id"]
        )
        end_messages: Dict[Optional[str], str] = {
            "bad_word": "That did not seem like proper Japanese with kana only.",
            "not_noun": "That is not a common noun.",
            "n_ending": "Words that end with ん or ン end the game.",
            None: "Looks good!",
        }
        await message.reply(end_messages[payload["end_type"]])

    @shiritori_check.help_embed
    async def shiritori_check_help_embed(self, help_command: HelpCommand) -> discord.Embed:
        embed: discord.Embed = discord.Embed(color=help_command.color)
        # pylint: disable=missing-format-attribute
        embed.set_author(name="{0.name} {0.signature}".format(self.shiritori_check))
        # pylint: enable=missing-format-attribute
        embed.description = (
            f"{self.shiritori_check.short_doc}\n\n"  # pylint: disable=no-member
            "The current implementation of Tango's Shiritori only allows hiragana and katakana to "
            "be used. Shiritori with kanji will be added in the future, with kana-only Shiritori "
            "being a game option.\n\n"
            "To learn how to play the game with Tango, type "
            f"`{help_command.context.prefix} help shiritori`."
        )
        embed.add_field(
            name="Command Aliases",
            value=" / ".join(self.shiritori_check.aliases),  # pylint: disable=no-member
        )
        embed.add_field(
            name="Check Conditions",
            value=(
                "1. The word is made up of valid hiragana or katakana syllables.\n"
                "2. Thee word does not end with with ん or ン.\n"
                "3. The word consists of at least two kana. (ああ but not アー)\n"
                "4. The word is a common noun in the Japanese language."
            ),
        )
        return embed


def setup(bot: botto.Botto) -> None:
    cog = Shiritori(bot)
    bot.add_cog(cog)
