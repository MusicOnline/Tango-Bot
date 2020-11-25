from discord.ext import commands

from .errors import NotConnectedToRestrictedApi


def require_restricted_api():
    def predicate(ctx):
        cog = ctx.bot.get_cog("RestrictedApi")
        if not cog or not cog.websocket:
            raise NotConnectedToRestrictedApi

    return commands.check(predicate)
