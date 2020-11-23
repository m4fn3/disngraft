import asyncio
import datetime
import json
import os
import random
import sys
import time

import aiofiles
import discord
import traceback2
from discord.ext import commands

from ProcManager import ProcManager
from bot import Bot
from enums import ServerStatus
from settings import *


def check_perm():
    """Check command executor's permission"""

    async def predicate(ctx):
        roles = {role.id for role in ctx.author.roles}
        if not SERVER_MANAGER_ROLE:  # if roles are empty, available for anyone
            return True
        elif roles & set(SERVER_MANAGER_ROLE):  # if user has one of specified role
            return True
        else:  # if user doesn't have required role
            return False

    return commands.check(predicate)


class Server(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        """Hook the errors on bot commands"""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f":x: You are using this command too quickly!\nTry again in {error.retry_after:.2f} seconds.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(":x: " + str(error))
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(":x: You don't have permission to use this command.")
        else:
            await ctx.send(f":x: Unexpected error has occurred.\n```py\n{str(error)[:1900]}```")

    @check_perm()
    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def start(self, ctx):
        """Command to start the minecraft server"""
        if self.bot.status != ServerStatus.STOPPED.value:
            await ctx.send(":x: Server is already running or starting!")
            return
        if (self.bot.wh_tunnel is None) or (self.bot.wh_log is None):
            await ctx.send(
                ":x: It seems I failed to initialize channel data.\n"
                "Make sure that bot have right permissions."
                "Restart program to apply settings after changing."
            )
            return
        await ctx.send(":hourglass_flowing_sand: Starting server...")
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game("Starting minecraft server..."))
        self.bot.status = ServerStatus.STARTING.value
        try:
            await self.run_server()
        except:
            await ctx.send(
                f":x: Following error has occurred when running minecraft server:\n"
                f"```java\n{traceback2.format_exc()}```"
            )
        finally:
            await self.bot.change_presence(status=discord.Status.dnd)
            self.bot.status = ServerStatus.STOPPED.value

    @check_perm()
    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def stop(self, ctx):
        """Command to stop the server"""
        if self.bot.status != ServerStatus.RUNNING.value:
            await ctx.send(":x: Server hasn't started yet!")
            return
        await self.bot.proc.stop()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def status(self, ctx):
        """Command to check the status of server"""
        embed = discord.Embed(title="Current Status", color=discord.Color.blue())
        # Build status string
        desc = f"`Host  :` {self.bot.host}\n"
        if self.bot.status == ServerStatus.STOPPED:
            desc += f"`Status:` :red_circle: STOPPED\n"
        elif self.bot.status == ServerStatus.STARTING:
            desc += f"`Status:` :yellow_circle: STARTING\n"
        elif self.bot.status == ServerStatus.RUNNING:
            desc += f"`Status:` :green_circle: RUNNING\n"
            # calc delta time
            td = datetime.timedelta(seconds=int(time.time() - self.bot.proc.uptime))
            m, s = divmod(td.seconds, 60)
            h, m = divmod(m, 60)
            d = td.days
            desc += f"`Online:` {len(self.bot.proc.members)}\n" \
                    f"`Member:` {','.join(self.bot.proc.members)}\n" \
                    f"`Uptime:` {d}d {h}h {m}m {s}s\n"
        desc += f"Powered by [mafusuke/disngraft](https://github.com/mafusuke/disngraft)"
        embed.description = desc
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def connect(self, ctx, player):
        """Command to connect account between Discord and MineCraft"""
        if self.bot.status != ServerStatus.RUNNING.value:
            await ctx.send(":x: Before connect your account, start the server!")
            return
        if player not in self.bot.proc.members:
            await ctx.send(":x: No such name player on the server.")
            return
        key = str(random.randint(1, 9999)).zfill(4)
        await self.bot.proc.send_key(player, key)  # tell the key in the server
        await ctx.send(f":incoming_envelope: I told the verify key to {player} in MineCraft chat!\nPlease check the key and simply type them here by 1minute.")
        try:
            msg = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=60)
            if msg.content != key:  # Key doesn't match
                await ctx.send(":x: Wrong key was provided! Failed to connect account.")
                return
            self.bot.accounts[str(ctx.author.id)] = player
            async with aiofiles.open(CONNECT_DATA_FILE, "w") as f:
                await f.write(json.dumps(self.bot.accounts))
            await ctx.send(f":white_check_mark: Your account connected to {player} successfully!")
        except asyncio.TimeoutError:
            await ctx.send(":x: Timeout! Now key became invalid.")

    @commands.is_owner()
    @commands.command()
    async def sh(self, ctx, *, script):
        """Run the given shell script"""
        process = await asyncio.create_subprocess_shell(
            script, shell=True, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE
        )
        result = await process.communicate()
        await ctx.send("\n".join([res.decode('utf-8') for res in result]))

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx):
        """Reload itself"""
        await ctx.send(":hourglass_flowing_sand: Restarting bot...")
        await self.bot.logout()

    @commands.is_owner()
    @commands.command()
    async def restart(self, ctx):
        """Restart program"""
        python = sys.executable
        os.chdir("..")  # back to disngraft folder
        os.execle(python, python, str(__file__).replace("server.py", "main.py"), *sys.argv, os.environ)

    async def run_server(self):
        """Run the minecraft server"""
        # run the start server command
        start_cmd = f"{JAVA_EXECUTABLE} -jar {'-Xmx' + MAX_MEM if MAX_MEM else ''} {'-Xms' + MAX_MEM if MIN_MEM else ''} {JAR_FILE} {'nogui' if NOGUI else ''}"
        proc = await asyncio.create_subprocess_shell(
            start_cmd,
            shell=True, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE
        )
        # Parse output
        pm = ProcManager(proc, self.bot)
        self.bot.proc = pm
        await pm.wait_output()
        self.bot.proc = None  # Reset proc after stopped


def setup(bot):
    bot.add_cog(Server(bot))
