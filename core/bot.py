import nest_asyncio
import logging
import asyncpg
import aiohttp
import mystbin
import random
import utils
import yaml
import ulid
import core
import os

from defectio.types.payloads import MessagePayload
from defectio.ext import commands, tasks
from typing import Optional, Any


nest_asyncio.apply()

logger = logging.getLogger('defectio')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='revolt.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Rodo(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.owner_id = "01FE6JZP6QDH5YKNHATCE0PDVH" # put your user id here

        self.myst = mystbin.Client()

        self.config = yaml.load(
            open("config.yaml"),
            Loader=yaml.Loader
        )
        self.db: asyncpg.Pool = self.loop.run_until_complete(
            asyncpg.create_pool(
                database="rodo",
                host="localhost",
                port="5432",
                user="rodo",
                password=self.config["DATABASE"]["PASSWORD"]
            )
        )

    @tasks.loop(seconds=10)
    async def update_status(self):
        await self.wait_until_ready()

        texts = [
            "storing",
            "watching",
            "guarding"
        ]

        count = (await self.db.fetchrow("SELECT count(*) FROM todo"))["count"]
        await self.user.edit(
            status=f"rodo help | {random.choice(texts).title()} {count} tasks"
        )

    async def get_context(self, message, *, cls=core.Context):
        return await super().get_context(message, cls=cls)

    async def initialize(self):
        async with aiohttp.ClientSession() as session:
            self.session = session

            self.update_status.start()

            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS todo (
                    user_id TEXT,
                    todo_id SERIAL,
                    description VARCHAR(128),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
                    PRIMARY KEY (user_id, todo_id)
                )
                """.strip()
            )
            await self.start(
                token=self.config.get("TOKEN")
            )

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        self.http.send_message = self.http_send_message

    async def http_send_message(
        self,
        channel_id: str,
        *,
        content: Optional[str] = None,
        attachments: Optional[list[str]] = None,
        replies: Optional[Any] = None,
    ) -> MessagePayload:
        path = f"channels/{channel_id}/messages"
        json = {"nonce": ulid.new().str}
        self.hidden = utils.iter_dict(self.config)
        if content is not None:
            for k, v in self.hidden.items():
                content = content.replace(v, f"[ {k} ]")
            json["content"] = content
        if attachments is not None and len(attachments) > 0:
            json["attachments"] = attachments
        if replies is not None:
            json["replies"] = replies
        return await self.http.request("POST", path, json=json)
    

bot = Rodo(
    command_prefix="rodo ",
    strip_after_prefix=True
)

for i in os.listdir("./cogs"):
    if not i.endswith(".py"):
        continue

    bot.load_extension(f"cogs.{i[:-3]}")