import asyncio
import defectio
import core
import re

from core.bot import Rodo
from defectio.ext import commands
from core.context import Context


class Todo(core.Cog):
    def __init__(self, bot):
        self.bot: Rodo = bot
        self.amount_regex = re.compile(r"(\d+)-(\d+)")
        self.time_str = "%d.%m.%y %H:%M:%S"

    @commands.command(description="Adds a todo task.")
    #@commands.cooldown(1, 5, commands.BucketType.user)
    async def add(self, ctx: Context, *, task: str):
        limit = 128
        if len(task) > limit:
            return await ctx.send(f"❌ Text cannot be longer than `{limit}` characters")

        result = await self.bot.db.fetchrow(
            """
            WITH rows AS (
                INSERT INTO todo (user_id, description)
                VALUES ($1, $2)
                RETURNING 1
            )
            SELECT count(*) FROM todo WHERE user_id = $1;
            """.strip(),
            ctx.author.id,
            task
        )
        count = result["count"]+1
        
        await ctx.send(f"✅ Added task {count} - `{task}`")

    @commands.command(description="Lists all todo tasks.")
    #@commands.cooldown(1, 5, commands.BucketType.user)
    async def list(self, ctx: Context, amount: str = "1-10"):
        reg = self.amount_regex.findall(amount)
        if not reg:
            return await ctx.send("❌ Invalid amount, please use something like `1-10`")
        start, end = int(reg[0][0])-1, int(reg[0][1])
        if start <= -1 or end <= -1:
            return await ctx.send("❌ Invalid amount, please use something like `1-10`")
        if end > 10:
            return await ctx.send("❌ Cannot show more than 10 tasks")
        if start >= end:
            return await ctx.send("❌ Start cannot be higher or equals to end")

        result = await self.bot.db.fetch(
            "SELECT * FROM todo WHERE user_id = $1",
            ctx.author.id
        )
        cut = result[start:end]

        if not result:
            return await ctx.send("❌ Could not find any tasks")

        text = "\n".join(
            f"{v['created_at'].strftime(self.time_str)} - {result.index(v)+1}: {v['description']}"
            for v in cut
        )

        await ctx.send(f"{len(result)} Tasks\n\n```\n{text}\n```")

    @commands.command(aliases=["delete"])
    #@commands.cooldown(1, 5, commands.BucketType.user)
    async def remove(self, ctx: Context, task: int):
        result = await self.bot.db.fetch(
            "SELECT * FROM todo WHERE user_id = $1",
            ctx.author.id
        )
        try:
            task_ = result[task-1]
        except IndexError:
            return await ctx.send("That task doesn't exist")
        else:
            await self.bot.db.execute("DELETE FROM todo WHERE todo_id = $1", task_["todo_id"])
        
        await ctx.send(f"Deleted task **{task}** (`{task_['description']}`)")

    @commands.command()
    #@commands.cooldown(1, 5, commands.BucketType.user)
    async def clear(self, ctx: Context):
        await ctx.send(
            f"<@{ctx.author.id}>, Are you sure you want to clear all of your tasks? "
            "Please type `yes` to accept or `no` to decline."
        )
        try:
            message = await self.bot.wait_for(
                "message",
                check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ["yes", "no"],
                timeout=15
            )
        except asyncio.TimeoutError:
            return
        if message.content.lower() == "no":
            return await ctx.send("Alright, cancelling...")
        
        if message.content.lower() == "yes":
            result = await self.bot.db.fetchrow(
                """
                WITH rows AS (
                    DELETE FROM todo WHERE user_id = $1
                    RETURNING 1
                )
                SELECT count(*) FROM todo WHERE user_id = $1;
                """.strip(),
                ctx.author.id
            )
            await ctx.send(f"✅ Cleared **{result['count']}** tasks.")

        

def setup(bot):
    bot.add_cog(Todo(bot))
