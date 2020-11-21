<img src="https://i.imgur.com/chUdF6x.png" width="250px">

# disngraft
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python: 3.8](https://img.shields.io/badge/Python-3.8-blue)

disngraft is discord bot based MineCraft server manager.

It allows you to get logs and share chats between Minecraft and Discord without any plugins.

Also it contains ngrok tunnel connection so that you don't have to open the router port.

# Requirements
- Python3.8.x
- Java

# Start Guide

1. Clone this repository.
   ```shell script
    git clone https://github.com/mafusuke/disngraft.git
    cd disngraft
    pip install -r requirements.txt
   ```

2. Create your Discord BOT.

    Go to [Discord Developer Portal](https://discord.com/developers/applications) and create by clicking *New Application*. 
    Then click *Add Bot* on Bot tab. 
    
    Turn on *SERVER MEMBERS INTENT* and copy TOKEN.
    
    Next open Oauth2 tab, click *bot* on *SCOPE* and *Administrator* on *BOT PERMISSIONS*. After that *Copy* your bot's invite url and add them into your server.
    
3. Get the TOKEN of Ngrok.
    
    SignUp on [Ngrok Dashboard](https://dashboard.ngrok.com/auth/your-authtoken) and you will see your TOKEN on Authentication tab.
    
4. Setup chat channel and console channel.

    Before this, you have to enable developer mode of Discord.
    
    Copy the ID of chanel that you want to receive console logs and ID of channel you want to receive chats.
    
5. Customize settings.
    
    Copy your TOKEN of ngrok and Discord BOT, channel ID of console channel and chat channel into settings.py
    
    Also you can customize settings by editing them. Descriptions are provided to each one as comment.
    
6. Prepare server jar file.
    
    Since it doesn't depends on MineCraft server's version, it doesn't contain server file.
    
    So you have to manually place your server files inside **server directory**.
    
    Here is sample directory structure:

    ```
    ./disngraft
    ├── LICENSE
    ├── ProcManager.py
    ├── README.md
    ├── disngraft.png
    ├── enums.py
    ├── main.py
    ├── regex_data.py
    ├── requirements.txt
    ├── server
    │   ├── banned-ips.json
    │   ├── banned-players.json
    │   ├── bukkit.yml
    │   ├── commands.yml
    │   ├── connect.json
    │   ├── eula.txt
    │   ├── help.yml
    │   ├── logs
    │   │   └── latest.log
    │   ├── ops.json
    │   ├── permissions.yml
    │   ├── server-icon.png
    │   ├── server.jar
    │   ├── server.properties
    │   ├── usercache.json
    │   ├── whitelist.json
    │   ├── world
    │   │   └── (Abbreviated)
    ├── server.py
    └── settings.py
    ```
    
7. Now ready to start!
    
   ```shell script
    python3 main.py
   ```
   If it says *Now Discord bot is ready to use!* you succeeded.
   
   Type `d?help` on your server to check usage of each command.
    
# Basic Usage
You can change BOT's prefix (default `d?`) on settings.py

`d?start` ... Start the MineCraft server

`d?stop` ... Stop the server

`d?status` ... Current status of the server

`d?connect <your MineCraft name>` ... Connect you account with MineCraft account
