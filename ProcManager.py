import asyncio
import datetime
import re
import time

import aiohttp
import discord
import traceback2

from bot import Bot
from enums import ServerStatus, Clr
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

        self.save_me = False
        self.uptime = time.time()
        self.members = []
        self.aiohttp_session = aiohttp.ClientSession()

    async def command_input(self, command):
        """Input commands to server"""
        self.stdin.write(
            f"{command}\n".encode()  # Convert string to bytes
        )
        try:
            await self.stdin.drain()
        except ConnectionResetError:
            return

    async def send_chat(self, sender: discord.User, content: str):
        """Send discord chat to MineCraft"""
        sender_name = sender.name
        if str(sender.id) in self.bot.accounts:  # If user connected their own account
            sender_name = self.bot.accounts[str(sender.id)]  # use their MineCraft name
        await self.command_input(
            'tellraw @a {"text": "<%s> %s"}' % (sender_name, content)
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
            output = output.strip()  # remove spaces to get high precision matching
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
                    print(traceback2.format_exc())
            else:  # If output is empty
                break
            if self.returncode is not None:  # If process is ended
                break
        if self.save_me:  # avoid github error of file lock
            self.bot.loop.create_task(self.save_server())

    async def parse_output(self, output: str):
        """Parse output texts from server"""
        if CONSOLE_CHANNEL:
            if re.fullmatch(self.regex.on_tell, output) is not None:
                return  # don't transfer content of tell command
            await self.send_log(output)
        if TUNNEL_CHANNEL:
            # Events
            if (match := re.fullmatch(self.regex.on_chat, output)) is not None:
                await self.on_chat(match.group(1), match.group(2))
            elif (match := re.fullmatch(self.regex.player_join, output)) is not None:
                await self.player_join(match.group(1))
            elif (match := re.fullmatch(self.regex.player_leave, output)) is not None:
                await self.player_leave(match.group(1))
            elif (match := re.fullmatch(self.regex.server_start, output)) is not None:
                await self.server_start(match.group(1))
            elif re.fullmatch(self.regex.server_stop, output) is not None:
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
            self.save_me = True

    async def save_server(self):
        """Push changes of server directory to Git"""
        print(f"Saving server data to GitHub...")
        process = await asyncio.create_subprocess_shell(
            f'pwd && git add . && git commit -m "{str(datetime.datetime.now()).replace(" ", "_")}" && git push',  # commit with now_time
            shell=True, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE
        )
        result = await process.communicate()
        print("\n".join([res.decode('utf-8') for res in result]))

    async def send_log(self, output):
        """Send console log"""
        # discord.py automatically try again after rate-limit failure
        # but for logs, we don't care about each logs carefully
        # so we prioritize performance
        await self.aiohttp_session.post(
            self.bot.wh_log.url,  # URL of console log chanel
            json={
                "content": output,  # main content
                "avatar_url": str(self.bot.user.avatar_url),  # use bot's avatar
                "username": "disngraft"
            },
            headers={
                'Content-Type': 'application/json'
            }
        )
