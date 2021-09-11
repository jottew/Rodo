import nest_asyncio
import asyncpg
import aiohttp
import utils
import yaml
import ulid
import core
import os

from defectio.types.payloads import MessagePayload
from defectio.ext import commands
from typing import Optional, Any


nest_asyncio.apply()


class Rodo(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.config = yaml.load(
            open("config.yaml"),
            Loader=yaml.Loader
        )

        self.db: asyncpg.Pool = self.loop.run_until_complete(
            asyncpg.create_pool(
                database="rodo",
                host="localhost",
                port="5432",
                user=self.config["DATABASE"]["USER"],
                password=self.config["DATABASE"]["PASSWORD"]
            )
        )

    async def get_context(self, message, *, cls=core.Context):
        return await super().get_context(message, cls=cls)

    async def initialize(self):
        async with aiohttp.ClientSession() as session:
            self.session = session

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
    command_prefix="rodo "
)

for i in os.listdir("./cogs"):
    if not i.endswith(".py"):
        continue

    bot.load_extension(f"cogs.{i[:-3]}")