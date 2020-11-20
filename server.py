import asyncio
from ProcManager import ProcManager

import discord
import traceback2
from discord.ext import commands

from enums import ServerStatus
from main import Bot
from settings import *


class Server(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()  # TODO: cool_downs and perm checking
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
        await ctx.send("Starting server...")
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

    @commands.command()
    async def stop(self, ctx):
        """Command to stop the server"""
        if self.bot.status != ServerStatus.RUNNING.value:
            await ctx.send(":x: Server hasn't started yet!")
            return
        await self.bot.proc.stop()

    @commands.command()
    async def status(self, ctx):
        """Command to check the status of server"""
        embed = discord.Embed(title="Current Status", color=discord.Color.blue())
        # Build status string
        status_text = ""
        if self.bot.status == ServerStatus.STOPPED:
            status_text = ":red_circle: STOPPED"
        elif self.bot.status == ServerStatus.STARTING:
            status_text = ":yellow_circle: STARTING"
        elif self.bot.status == ServerStatus.RUNNING:
            status_text = ":green_circle: RUNNING"
        embed.description = f"`Status:` {status_text}\n" \
                            f"`Host  :` {self.bot.host}"
        await ctx.send(embed=embed)

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
