import logging
import os
import asyncio
import threading
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from commands.start import start
from commands.help import help
from commands.projects import handle, button
from ai_agent.ai import ask_groq

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# FastAPI app
web_app = FastAPI(title="Antenhe Assistant API")

web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI Request model
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

        # Use HTTPX explicitly if needed (to avoid httpcore bugs)
        answer = ask_groq(request.question)
        return {
            "status": "success",
            "answer": answer,
            "truncated": len(answer) >= 1024
        }
    except httpx.RequestError as e:
        logger.error(f"HTTPX Request failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def run_fastapi():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(web_app, host="0.0.0.0", port=port)

# Telegram error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Unhandled error: {context.error}", exc_info=True)

# Initialize bot commands
async def on_startup(application):
    await application.bot.set_my_commands([
        ("start", "Start the bot"),
        ("help", "Show help info"),
        ("projects", "Show Antenhe's projects"),
        ("ask", "Ask the AI about Antenhe Sileshi"),
    ])
    logger.info("✅ Bot commands initialized")

# Main launcher
def main():
    # Run FastAPI on a separate thread
    threading.Thread(target=run_fastapi, daemon=True).start()

    # Start Telegram bot
    app = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .post_init(on_startup) \
        .concurrent_updates(False) \
        .build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("projects", handle))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(error_handler)

    logger.info("🚀 Starting Telegram bot...")
    app.run_polling(
        poll_interval=2.0,
        timeout=30,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
