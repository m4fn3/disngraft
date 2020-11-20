"""
Custom Settings.

In here 'blank' means, replace with "" or None
"""

# Minecraft
JAVA_EXECUTABLE = "java"  # path to java
SERVER_DIR = "./server"  # path to server folder
JAR_FILE = "server.jar"  # filename of minecraft server jar file, it will be estimated that file exists on SERVER_DIR
NOGUI = True  # whether show gui or not
MAX_MEM = "4G"  # max memory quota of java runtime
MIN_MEM = ""  # min memory quota of java runtime
SAVE_SERVER = False  # commit and push server directory for saving world. To use this, SERVER_DIR should be under git management

# Discord Bot
BOT_TOKEN = ""  # type your discord bot token in the bracket
BOT_PREFIX = "d?"  # prefix for the bot
TUNNEL_CHANNEL = 718471668573667478  # tunnel channel to talk between minecraft and discord. leave blank to disable
CONSOLE_CHANNEL = 768123203351740416  # console channel to send logs.  leave blank to disable
CUSTOM_HOST = None  # custom server host name for bot's presence. leave blank to set ngrok url.

# Ngrok
USE_NGROK = True  # whether enable ngrok or not
NGROK_TOKEN = ""  # type your ngrok token in the bracket
NGROK_REGION = "us"  # "us", "eu", "ap", "au", "sa", "jp" and "in" is available
TUNNEL_PORT = 25565  # port that your minecraft server will be running on. make sure that you're using same port number with server.properties one
