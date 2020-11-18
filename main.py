import os
import subprocess

import discord
from discord.ext import commands
from pyngrok import ngrok, conf

from settings import *


class Bot(commands.Bot):
    def __init__(self, prefix, intents):
        super().__init__(prefix, intents=intents)

        self.host = None

        self.load_extension("server")

    async def on_ready(self):
        print(f"Successfully logged in to {self.user}\nNow Discord bot is ready to use!")
        if USE_NGROK:
            await self.create_tunnel()

    async def create_tunnel(self):
        conf.get_default().region = NGROK_REGION
        ngrok.set_auth_token(NGROK_TOKEN)
        tunnel = ngrok.connect(TUNNEL_PORT, "tcp")
        self.host = tunnel.public_url.replace("tcp://", "")
        await self.change_presence(status=discord.Status.online, activity=discord.Game(self.host))

    async def run_server(self):
        cmd = f"{JAVA_EXECUTABLE} -jar {'-Xmx' + MAX_MEM if MAX_MEM else ''} {'-Xms' + MAX_MEM if MIN_MEM else ''} {JAR_FILE} {'nogui' if NOGUI else ''}"
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            output = proc.stdout.readline()
            if output:
                yield output

            if not output and proc.poll() is not None:
                break


if __name__ == "__main__":
    bot = Bot(BOT_PREFIX, intents=discord.Intents.all())
    bot.run(BOT_TOKEN)
