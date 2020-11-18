from discord.ext import commands
from main import Bot

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

def setup(bot):
    bot.add_cog(Server(bot))
