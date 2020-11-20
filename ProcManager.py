import asyncio
import datetime
import re
import time

import discord

from enums import ServerStatus, Clr
from main import Bot
from regex_data import LogRegex
from settings import *


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

        self.uptime = time.time()
        self.members = []

    async def command_input(self, command):
        """Input commands to server"""
        self.stdin.write(
            f"{command}\n".encode()  # Convert string to bytes
        )
        await self.stdin.drain()

    async def send_chat(self, sender: discord.User, content: str):
        """Send discord chat to MineCraft"""
        sender_name = sender
        if str(sender.id) in self.bot.accounts:  # If user connected their own account
            sender_name = self.bot.accounts[str(sender.id)]  # use their MineCraft name
        await self.command_input(
            f"say <{sender_name}> {content}"
        )

    async def stop(self):
        """Stop the server"""
        await self.command_input(
            "stop"
        )

    async def send_key(self, player, key):
        """Send verify key to specific player"""
        await self.command_input(
            f"tell {player} {key}"
        )

    async def wait_output(self):
        """Wait for output"""
        cache = []
        while True:
            output = await self.stdout.readline()
            output = output.decode("utf-8")
            # For avoiding rate limit, embed 5 logs per message
            if self.bot.status != ServerStatus.RUNNING.value:
                if "[Server thread/INFO]: Done" in output:  # If log contains Done, pass the stock
                    pass
                else:
                    if "%" in output:  # it still be too many so we ignore log that contains %
                        continue
                    cache.append(output)
                    if len(cache) == 5:  # release stock
                        output = "".join(cache)
                        cache.clear()  # reset stock
                    else:  # haven't reached log count to 5
                        continue
            if output:  # Parse output
                try:
                    await self.parse_output(output)  # Convert from bytes to str
                except:
                    print(f"{Clr.RED}[!] Error has occurred on analysing output: {output}{Clr.END}")
            else:  # If output is empty
                break
            if self.returncode is not None:  # If process is ended
                break

    async def parse_output(self, output: str):
        """Parse output texts from server"""
        if CONSOLE_CHANNEL:
            if re.match(self.regex.on_tell, output) is not None:
                return  # we don't transfer content of tell command
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
        unique_avatar = None
        if senders := [k for k, v in self.bot.accounts.items() if v == sender]:  # If user connected their own account
            user = self.bot.get_user(int(senders[0]))
            if user is not None:  # user was not found on the internal cache
                unique_avatar = user.avatar_url  # Use their own Discord avatar and name
                sender = user.name
        await self.bot.wh_tunnel.send(content, avatar_url=unique_avatar if unique_avatar else self.bot.user.avatar_url, username=sender)

    async def player_join(self, player):
        """On player join"""
        self.members.append(player)
        embed = discord.Embed(title=f"{player} has joined", color=discord.Color.green())
        await self.bot.wh_tunnel.send(embed=embed, avatar_url=self.bot.user.avatar_url, username="disngraft")
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.bot.host} | {len(self.members)} players"))

    async def player_leave(self, player):
        """On player leave"""
        self.members.remove(player)
        embed = discord.Embed(title=f"{player} has left", color=discord.Color.red())
        await self.bot.wh_tunnel.send(embed=embed, avatar_url=self.bot.user.avatar_url, username="disngraft")
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.bot.host} | {len(self.members)} players"))

    async def server_start(self, spend_time):
        """On start server"""
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.bot.host} | 0 players"))
        self.bot.status = ServerStatus.RUNNING.value
        embed = discord.Embed(title=f"Successfully started the server! ({spend_time})", color=discord.Color.blue())
        await self.bot.wh_tunnel.send(embed=embed, avatar_url=self.bot.user.avatar_url, username="disngraft")

    async def server_stop(self):
        """On stop server"""
        embed = discord.Embed(title=f"Server stopped!", color=discord.Color.blue())
        await self.bot.wh_tunnel.send(embed=embed, avatar_url=self.bot.user.avatar_url, username="disngraft")
        if SAVE_SERVER:
            await asyncio.create_subprocess_shell(
                f'git add . && git commit -m "{str(datetime.datetime.now()).replace(" ", "_")}" && git push',  # commit with now_time
                shell=True, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE
            )
