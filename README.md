# Telegram Transcript Bot

This project is a Telegram bot that helps users upload transcripts, process courses, and manage their academic progress. The bot uses Redis for session state management and Telegram's API for interacting with users.

## Project Structure

- `data/`: Contains JSON files for the bot data and course credits.
- `src/`: Contains the source code for the bot, including handlers, utilities, and the main application script.
- `.env`: Environment variables for Redis and Telegram.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/telegram-bot.git
   cd telegram-bot
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a .env file with the following variables:
   ```
   REDIS_HOST=
   REDIS_PORT=
   REDIS_PASSWORD=
   TOKEN=
   CHAT_ID=
   ```

## Running the Bot

1. Load the environment variables:

   ```bash
   source .env
   ```

2. Run the bot locally:

   ```bash
   python src/bot.py
   ```

## Dependencies

- python-telegram-bot
- redis
- pdfplumber
- python-dotenv
