# Discord to Telegram Notifier

A Discord bot that tracks voice channel activity and scheduled events, then sends notifications to Telegram channels.

## Description

This application monitors Discord guilds for:
- Users joining/leaving voice channels
- Scheduled events being created or deleted
- Sends real-time notifications to configured Telegram chats

## Features

### Discord Bot Commands
- **Voice Channel Tracking**: Automatically detects when users join or leave voice channels
- **Scheduled Events**: Monitors creation and deletion of Discord scheduled events
- **Multi-Guild Support**: Can track multiple Discord guilds simultaneously

### Telegram Bot Commands
- `/start` or `/help` - Display help information
- `/add_channel [Guild_Name]` - Add a Discord guild to tracking in the current chat
- `/remove_channel [Guild_Name]` - Remove a Discord guild from tracking
- `/get_ip` - Get the current chat ID

## File Structure

```
├── notifier_ds.py          # Discord bot implementation
├── notifier_tg.py          # Telegram bot implementation  
├── main.py                 # Main entry point
├── launch_ds.py            # Discord bot launcher
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Docker image definition
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

1. Create a `.env` file with:
   ```
   TOKEN_TG=your_telegram_bot_token
   TOKEN=your_discord_bot_token
   DATABASE_PW=your_database_password
   PORT=5432
   ```

2. Add the Discord bot to your guild using the OAuth2 link
3. Start a chat with the Telegram bot and use `/add_channel [Guild_Name]`

## Running

### Docker (Recommended)
```bash
docker-compose up -d
```

### Local Development
```bash
python main.py
```

## Architecture

- **Discord Bot**: Listens for voice state updates and scheduled event changes
- **Telegram Bot**: Handles user commands and sends notifications
- **PostgreSQL**: Stores tracking configurations
- **Docker**: Containerized deployment with docker-compose orchestration
