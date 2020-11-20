import asyncio
import discord
import re

from main import Bot
from regex_data import LogRegex
from settings import *
from enums import ServerStatus, Clr


class ProcManager:
    """MineCraft server process manager"""
    def __init__(self, proc: asyncio.subprocess.Process, bot: Bot):
        self.bot = bot

        self.proc = proc
        self.stdout = proc.stdout
        self.stderr = proc.stderr
        self.stdin = proc.stdin
        self.returncode = proc.returncode

        self.regex = LogRegex()

    async def command_input(self, command):
        """Input commands to server"""
        self.stdin.write(
            f"{command}\n".encode()  # Convert string to bytes
        )
        await self.stdin.drain()

    async def send_chat(self, sender, content):
        """Send discord chat to MineCraft"""
        # TODO: look for connected mc's name
        await self.command_input(
            f"/say <{sender}> {content}"
        )

    async def wait_output(self):
        """Wait for output"""
        while True:
            output = await self.stdout.readline()
            if output:
                try:
                    await self.parse_output(output.decode('utf-8'))  # Convert from bytes to str
                except:
                    print(f"{Clr.RED}[!] Error has occurred on analysing output: {output}{Clr.END}")
            else:  # If output is empty
                break
            if self.returncode is not None:  # If process is ended
                break

    async def parse_output(self, output: str):
        """Parse output texts from server"""
        if "[Server thread/INFO]: Preparing spawn area:" in output:
            return
        if CONSOLE_CHANNEL:
            await self.bot.wh_log.send(output, avatar_url=self.bot.user.avatar_url, username="disngraft")
        if TUNNEL_CHANNEL:
            # Events
            if (match := re.match(self.regex.on_chat, output)) is not None:
                await self.on_chat(match.group(1), match.group(2))
            elif (match := re.match(self.regex.player_join, output)) is not None:
                await self.player_join(match.group(1))
            elif (match := re.match(self.regex.player_leave, output)) is not None:
                await self.player_leave(match.group(1))
            elif (match := re.match(self.regex.server_start, output)) is not None:
                await self.server_start(match.group(1))
            elif re.match(self.regex.server_stop, output) is not None:
                await self.server_stop()

    async def on_chat(self, sender, content):
        """On receive chat"""
        # TODO: look for connected user's own icon
        await self.bot.wh_tunnel.send(content, avatar_url=self.bot.user.avatar_url, username=sender)

    async def player_join(self, player):
        """On player join"""
        embed = discord.Embed(title=f"{player} has joined", color=discord.Color.green())
        await self.bot.wh_tunnel.send(embed=embed, avatar_url=self.bot.user.avatar_url, username="disngraft")

    async def player_leave(self, player):
        """On player leave"""
        embed = discord.Embed(title=f"{player} has left", color=discord.Color.red())
        await self.bot.wh_tunnel.send(embed=embed, avatar_url=self.bot.user.avatar_url, username="disngraft")

    async def server_start(self, time):
        """On start server"""
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.bot.host} | 0 players | 0 minutes"))
        self.bot.status = ServerStatus.RUNNING.value
        embed = discord.Embed(title=f"Successfully started the server! ({time})", color=discord.Color.blue())
        await self.bot.wh_tunnel.send(embed=embed, avatar_url=self.bot.user.avatar_url, username="disngraft")

    async def server_stop(self):
        """On stop server"""
        embed = discord.Embed(title=f"Server stopped!", color=discord.Color.blue())
        await self.bot.wh_tunnel.send(embed=embed, avatar_url=self.bot.user.avatar_url, username="disngraft")
        # TODO: Option for saving world to GitHub
