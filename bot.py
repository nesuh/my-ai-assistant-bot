import logging
import os
import asyncio
import threading
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import telegram
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from commands.start import start
from commands.help import help
from commands.projects import handle, button
from ai_agent.ai import ask, ask_groq

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# FastAPI setup
web_app = FastAPI(title="Antenhe Assistant API")

# CORS middleware
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None

@web_app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "Antenhe Assistant",
        "version": "1.0",
        "endpoints": {
            "/api/ask": "POST - Ask questions about Antenhe"
        }
    }

@web_app.post("/api/ask")
async def api_ask_endpoint(request: QuestionRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        answer = ask_groq(request.question)
        return {
            "status": "success",
            "answer": answer,
            "truncated": len(answer) >= 1024
        }
    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def run_fastapi():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        web_app,
        host="0.0.0.0",
        port=port,
        log_config=None,
        access_log=False
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle Telegram bot errors"""
    error = context.error
    if isinstance(error, telegram.error.Conflict):
        logger.warning("Conflict detected - restarting polling")
        await asyncio.sleep(5)
        await context.application.updater.stop()
        await context.application.updater.start_polling()
    else:
        logger.error(f"Unhandled error: {error}", exc_info=True)

async def on_startup(app):
    """Initialize bot commands"""
    await app.bot.set_my_commands([
        ("start", "Start the bot"),
        ("help", "Show help info"),
        ("projects", "Show Antenhe's projects"),
        ("ask", "Ask the AI about Antenhe Sileshi"),
    ])
    logger.info("Bot commands initialized")

def main():
    # Start FastAPI in separate thread
    server_thread = threading.Thread(target=run_fastapi, daemon=True)
    server_thread.start()

    # Configure bot with conflict prevention
    app = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .post_init(on_startup) \
        .concurrent_updates(False) \
        .http_version("1.1") \
        .get_updates_http_version("1.1") \
        .build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("projects", handle))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("ask", ask))
    app.add_error_handler(error_handler)

    # Start polling with conflict-resistant settings
    logger.info("Starting bot with conflict-resistant polling...")
    app.run_polling(
        poll_interval=2.0,
        timeout=30,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        close_loop=False,
        stop_signals=[]
    )

if __name__ == "__main__":
    main()