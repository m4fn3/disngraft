import json
import os
from typing import Optional

import discord
from discord.ext import commands
from pyngrok import ngrok, conf

from enums import ServerStatus, Clr
from settings import *


class Bot(commands.Bot):
    def __init__(self, prefix, intents, status):
        super().__init__(prefix, intents=intents, status=status)

        self.is_first_time = True

        self.host = CUSTOM_HOST or None
        self.status = ServerStatus.STOPPED.value
        self.proc = None

        self.accounts = {}
        self.load_connected_accounts()

        self.wh_tunnel: Optional[discord.Webhook] = None
        self.wh_log: Optional[discord.Webhook] = None

        self.load_extension("server")

    def load_connected_accounts(self):
        """Load connected accounts data"""
        if os.path.isfile(CONNECT_DATA_FILE):
            with open(CONNECT_DATA_FILE, "r") as f:  # load file
                self.accounts = json.load(f)  # load connected accounts data
        else:  # no such file
            with open(CONNECT_DATA_FILE, 'w') as f:
                json.dump({}, f)  # create file
            self.accounts = {}

    def clean_input(self, text):
        """Format text for minecraft"""
        return text.replace("\n", " ").lstrip("/") if text != "" else "%Temp%"

    async def on_ready(self):
        """Discord internal cache is ready"""
        if self.is_first_time:  # on_ready can be called multiple times
            self.is_first_time = False
            print(f"{Clr.GREEN}[O] Successfully logged in to {self.user}\nNow Discord bot is ready to use!{Clr.END}")
            await self.prepare_webhook()
            if USE_NGROK:
                await self.create_tunnel()

    async def on_message(self, message):
        """On message on Discord"""
        if message.author.bot:  # Skip bot's message to avoid forever loop
            return
        if self.status == ServerStatus.RUNNING.value:
            if message.channel.id == TUNNEL_CHANNEL:
                await self.proc.send_chat(message.author, self.clean_input(message.content))
            elif message.channel.id == CONSOLE_CHANNEL:
                await self.proc.command_input(self.clean_input(message.content))
        await self.process_commands(message)

    async def prepare_webhook(self):
        """Get webhook for sending logs in Discord"""
        if TUNNEL_CHANNEL:
            try:
                tch = self.get_channel(TUNNEL_CHANNEL)
                if tch is None:
                    raise
                # Get webhook of tunnel channel
                if (twh := discord.utils.get(await tch.webhooks(), name="disngraft")) is not None:
                    self.wh_tunnel = twh
                else:
                    self.wh_tunnel = await tch.create_webhook(name="disngraft")
            except:
                print(
                    f"{Clr.RED}[!] Failed to get tunnel channel.\n"
                    f"Make sure that bot is on the guild and have right permissions.{Clr.END}"
                )
        else:
            self.wh_tunnel = "N/A"
        if CONSOLE_CHANNEL:
            try:
                cch = self.get_channel(CONSOLE_CHANNEL)
                if cch is None:
                    print(
                        f"{Clr.RED}[!] Failed to get console channel.\n"
                        f"Make sure that bot is on the guild and have right permissions.{Clr.END}"
                    )
                    return
                # Get webhook of console channel
                if (cwh := discord.utils.get(await cch.webhooks(), name="disngraft")) is not None:
                    self.wh_log = cwh
                else:
                    self.wh_log = await cch.create_webhook(name="disngraft")
            except:
                print(
                    f"{Clr.RED}[!] Failed to get console channel.\n"
                    f"Make sure that bot is on the guild and have right permissions.{Clr.END}"
                )
        else:
            self.wh_log = "N/A"

    async def create_tunnel(self):
        """Open ngrok tcp tunnel"""
        conf.get_default().region = NGROK_REGION
        # conf.get_default().monitor_thread = False  # To ignore warnings
        ngrok.set_auth_token(NGROK_TOKEN)
        try:
            tunnel = ngrok.connect(TUNNEL_PORT, "tcp")
            self.host = CUSTOM_HOST or tunnel.public_url.replace("tcp://", "")
            print(f"{Clr.GREEN}[O] Successfully created ngrok tunnel{Clr.END} localhost:{TUNNEL_PORT} -> {self.host}")
        except:
            self.host = CUSTOM_HOST or "N/A"
            print(f"{Clr.RED}[!] Error has occurred on creating ngrok tunnel.")


if __name__ == "__main__":
    os.chdir(SERVER_DIR)  # move to the server directory

    print("Starting Discord Bot...")
    bot = Bot(BOT_PREFIX, intents=discord.Intents.all(), status=discord.Status.dnd)
    bot.run(BOT_TOKEN)  # start the bot
