# notifier_ds_tg
Script for sending updates and notifications from discord channel to telegram channel

What actions can it do?

1) In your Telegram App, find my Bot @NotifierFrogsBot ; Start a chat with Bot or add it in already existing chat
2) In your Discord Guild add the bot via link: https://discord.com/oauth2/authorize?client_id=1283029091993518110
3) Now you can set up notifications from Discord Guild into your telegram chat:
4) In Telegram chat with NotifierFrogsBot /add_channel NAME_OF_GUILD - all connections and disconections to the voice channels will be tracking from this Guild
5) /remove_channel - remove Guild from tracking
6) You can add multiple guilds to track in one chat
7) One guild can be tracked in multiple Telegram channels

CREATE .env

TOKEN_TG = "YOUR TELEGRAM BOT TOKEN"

TOKEN = "YOUR DISCORD BOT TOKEN"

DATABASE_PW = "Your database password"

PORT = "port"

To run: 
docker-compose up --build

