import logging
import os
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
from commands.start import start
from commands.help import help
from commands.projects import handle, button
from ai_agent.ai import ask
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading

# Load env variables
load_dotenv()

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

web_app = FastAPI()

# Add CORS middleware
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@web_app.get("/")
async def health_check():
    return {"status": "ok", "service": "Telegram Bot"}

def run_fastapi():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(web_app, host="0.0.0.0", port=port)

async def on_startup(app):
    await app.bot.set_my_commands([
        ("start", "Start the bot"),
        ("help", "Show help info"),
        ("projects", "Show Antenhe's projects"),
        ("ask", "Ask the AI about Antenhe Silesh"),
    ])

def main():
    # Start FastAPI server in a separate thread
    server_thread = threading.Thread(target=run_fastapi)
    server_thread.daemon = True
    server_thread.start()

    # Build and run Telegram bot
    app = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .post_init(on_startup) \
        .build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("projects", handle))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("ask", ask))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()