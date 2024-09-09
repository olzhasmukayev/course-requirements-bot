from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.handlers import start, handle_transcript, handle_kazakh_level, handle_major
import os

async def run_application():
    application = Application.builder().token(os.getenv("TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_transcript))
    application.add_handler(MessageHandler(filters.TEXT, handle_kazakh_level))
    application.add_handler(MessageHandler(filters.TEXT, handle_major))

    return application

def lambda_handler(event, context):
    asyncio.run(run_application())
    return {"statusCode": 200, "body": "Update processed successfully"}
