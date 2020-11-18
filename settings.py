# Minecraft
JAVA_EXECUTABLE = "java"  # path to java
JAR_FILE = "server.jar"  # filename of minecraft server jar file
NOGUI = True  # whether show gui or not
MAX_MEM = "4G"  # max memory quota of java runtime
MIN_MEM = ""  # min memory quota of java runtime

# Discord Bot
BOT_TOKEN = ""  # type your discord bot token in the bracket
BOT_PREFIX = "mc!"  # prefix for the bot
TUNNEL_CHANNEL = 718471668573667478  # tunnel channel to talk between minecraft and discord

# Ngrok
USE_NGROK = True  # whether enable ngrok or not
NGROK_TOKEN = ""  # type your ngrok token in the bracket
NGROK_REGION = "us"  # "us", "eu", "ap", "au", "sa", "jp" and "in" is available
TUNNEL_PORT = 25565  # port that your minecraft server will be running on. make sure that you're using same port number with server.properties one
