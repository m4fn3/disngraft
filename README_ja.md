<img src="https://i.imgur.com/chUdF6x.png" width="250px">

# disngraft
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python: 3.8](https://img.shields.io/badge/Python-3.8-blue)

disngraftはdiscordBOTベースのマインクラフトサーバー管理システムです。

これによりプラグイン無しで、ログ、チャットをDiscord-MineCraft間で同期できます。

またオプションでNgrok接続もサポートしているため、ポート開放無しでサーバーを外部公開することもできます。

# 要件
- Python3.8.x
- Java

# 使い方

1. このリポジトリをダウンロード
   ```shell script
    git clone https://github.com/mafusuke/disngraft.git
    cd disngraft
    pip install -r requirements.txt
   ```

2. DiscordBOTの作成

    [Discord Developer Portal](https://discord.com/developers/applications) に行き、*New Application*を押して新規アプリケーションを作成します。 
    その後、Botタブの*Add Bot*を押してBOTを作成します。
    
    *SERVER MEMBERS INTENT*欄を有効化して、トークンをコピーします。
    
    次にOauth2タブを開き、*SCOPE*で*bot*を押して、*BOT PERMISSIONS*の*Administrator*を押します。 その後*Copy*を押してBOTの招待リンクを取得し、あなたのサーバーに追加してください。    
    
3. Ngrokトークンの取得 (オプション)
    
    [Ngrok Dashboard](https://dashboard.ngrok.com/auth/your-authtoken) にログインまたは登録すると、Authenticationタブ上でトークンを確認できます。
    
4. チャットとログチャンネルの設定

    ※これを行う前にDiscordの開発者モードをオンにする必要があります。
    
    ログ、チャットを受け取りたいチャンネルのIDをそれぞれコピーします。
    
5. その他の設定
    
    settings.py内にDiscordBOTとNgrokのトークン及びチャンネルIDを書き込みます。
    
    また他の設定も変更することで、システムの挙動をカスタマイズすることができます。
    
6. jarファイル(マインクラフトサーバー本体)の準備
    
    このシステムはMineCraftのバージョンに依存しない設計のため、マインクラフトサーバーファイルを含んでいません。
    
    ディレクトリ構造の一例:

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
    
7. 起動の準備が完了しました
    
   ```shell script
    python3 main.py
   ```
   *Now Discord bot is ready to use!* と表示されれば成功です。
   
   サーバー上で`d?help`と入力して使い方を確認してください。
    
# 基本の使い方
BOTのプレフィックスはsettings.py内で自由に変更することができます (初期設定では`d?`)

`d?start` ... マインクラフトサーバーを起動

`d?stop` ... サーバーを停止

`d?status` ... 現在のサーバーのステータスを表示

**~~_``~~~~__~~~~__``_~~**`d?connect <your MineCraft name>` ... DiscordのアカウントとMineCraftのアカウントを連携設定
