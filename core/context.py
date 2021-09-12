import defectio
import discord
import core

from defectio.ext import commands

class Context(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = 0xff0000

    async def send(self, content: str = None, cache: bool = True, *args, **kwargs):
        if content is not None:
            mod = discord.utils.remove_markdown(content).strip()
            if len(content) > 2000:
                content = str(
                    await self.bot.myst.post(
                        mod
                    )
                )

        return await super().send(content, *args, **kwargs)