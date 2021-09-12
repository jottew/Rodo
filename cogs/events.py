import defectio
import utils
import core
import re

from core.bot import Rodo
from defectio.ext import commands
from core.context import Context


class Events(core.Cog):
    def __init__(self, bot):
        self.bot: Rodo = bot
        self.BadArgumentRegex = re.compile(r"Converting to \"(.+)\" failed for parameter \"(.+)\"\.")
        self.BadArgumentRegex2 = re.compile(r"with base \d+: \'?([^\']+)\'?")

    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx: Context, error: Exception):
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if ctx.command is not None:
            if hasattr(ctx.command, "on_error") or hasattr(ctx.bot.get_cog(ctx.command.cog_name), "on_error"):
                return

        if isinstance(error, commands.CommandOnCooldown):
            if await ctx.bot.is_owner(ctx.author):
                return await ctx.reinvoke()

            return await ctx.send(f"❌ Try again in {utils.time(int(error.retry_after))}")

        if isinstance(error, commands.MissingRequiredArgument):
            param = str(error.param).split(":")[0].replace(" ", "")
            return await ctx.send(f"❌ **{param}** is a required argument that is missing")

        if isinstance(error, commands.MaxConcurrencyReached):
            return await ctx.send(f"❌ {error.args[0]}")

        if isinstance(error, commands.MissingRequiredFlag):
            return await ctx.send(f"❌ **{error.flag.name}** is a required flag that is missing")

        if isinstance(error, commands.BadArgument):
            matches = self.BadArgumentRegex.findall(str(error))[0]
            type_ = matches[0]
            param = matches[1]
            actual = self.BadArgumentRegex2.findall(str(error.__cause__))[0]

            types = {
                "int": "number",
                "float": "number"
            }
            type_ = types.get(type_, type_)
            return await ctx.send(f"❌ Expected a {type_} for {param} parameter, but got `{actual}`")

        if isinstance(error, commands.MemberNotFound):
            return await ctx.send("❌ That member was not found")

        if isinstance(error, commands.BadUnionArgument):
            return await ctx.send("❌ Invalid parameters passed")

        if isinstance(error, commands.MissingPermissions):
            if await ctx.bot.is_owner(ctx.author):
                return await ctx.reinvoke()
            perms = utils.format_list(error.missing_permissions, seperator="and", brackets="`")
            return await ctx.send(f"❌ You are missing {perms} permissions")

        if isinstance(error, commands.BotMissingPermissions):
            perms = utils.format_list(error.missing_permissions, seperator="and", brackets="`")
            return await ctx.send(f"❌ I am missing {perms} permissions")

        if isinstance(error, commands.NotOwner):
            return await ctx.send(f"❌ Only my owner can do that >:(")

        if isinstance(
            error, (
                commands.CheckAnyFailure,
                commands.CheckFailure,
                commands.CommandNotFound)):
            return

        return await ctx.send(
            f"Some weird error occured, you can send it to my developer, if you want\n```py\n{error.__class__.__name__}: {str(error)}\n```"
        )

def setup(bot):
    bot.add_cog(Events(bot))
