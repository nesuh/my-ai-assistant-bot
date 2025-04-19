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

# Load env variables
load_dotenv()

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Async startup function to set bot commands
async def on_startup(app):
    await app.bot.set_my_commands([
        ("start", "Start the bot"),
        ("help", "Show help info"),
        ("projects", "Show Antenhe's projects"),
        ("ask", "Ask the AI about Antenhe Silesh"),
    ])

# Build app
app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("projects", handle))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("ask", ask))

print("🤖 Bot is running...")
app.run_polling()
