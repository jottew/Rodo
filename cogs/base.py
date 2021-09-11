import defectio
import core

from core.bot import Rodo
from defectio.ext import commands
from core.context import Context


class Base(core.Cog):
    def __init__(self, bot):
        self.bot: Rodo = bot

def setup(bot):
    #bot.add_cog(Base(bot))
    pass
