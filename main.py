import asyncio
import importlib
import os

import discord
from pyngrok import ngrok, conf

import bot
from enums import Clr
from settings import *


def create_tunnel():
    """Open ngrok tcp tunnel"""
    conf.get_default().region = NGROK_REGION
    ngrok.set_auth_token(NGROK_TOKEN)
    try:  # Create new tunnel
        tunnel = ngrok.connect(TUNNEL_PORT, "tcp")
        server_host = CUSTOM_HOST or tunnel.public_url.replace("tcp://", "")
        print(f"{Clr.GREEN}[O] Successfully created ngrok tunnel{Clr.END} localhost:{TUNNEL_PORT} -> {server_host}")
    except:
        server_host = CUSTOM_HOST or "N/A"
        print(f"{Clr.RED}[!] Error has occurred on creating ngrok tunnel.{Clr.END}")
    return server_host


if __name__ == "__main__":
    os.chdir(SERVER_DIR)  # move to the server directory

    host = None
    if USE_NGROK:  # create ngrok tunnel
        host = create_tunnel()

    print("Starting Discord Bot...")
    loop = asyncio.get_event_loop()
    while True:
        try:  # start bot
            disngraft = bot.Bot(BOT_PREFIX, host, intents=discord.Intents.all(), status=discord.Status.dnd)
            loop.run_until_complete(disngraft.start(BOT_TOKEN))
        except KeyboardInterrupt:
            break
        except:  # reload bot code too
            importlib.reload(bot)
            continue
