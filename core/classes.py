from typing import List
from defectio.ext import commands

class Cog(commands.Cog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        print(f"{self.qualified_name} has loaded")

def command(
    name = None,
    *,
    aliases = [],
    usage = None,
    description = "Command undocumented.",
    **kwargs
    ):

    cooldown_after_parsing = kwargs.pop("cooldown_after_parsing", True)

    return commands.command(
        name=name,
        aliases=aliases,
        usage=usage,
        cooldown_after_parsing=cooldown_after_parsing,
        description=description,
        **kwargs
    )

def group(
    name = None,
    *,
    aliases = [],
    usage = None,
    description = "Command group undocumented.",
    **kwargs
    ):

    cooldown_after_parsing = kwargs.pop("cooldown_after_parsing", True)

    return commands.group(
        name=name,
        aliases=aliases,
        usage=usage,
        cooldown_after_parsing=cooldown_after_parsing,
        description=description,
        **kwargs
    )