import logging
import os
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
from commands.start import start
from commands.help import help
from commands.projects import handle, button
from ai_agent.ai import ask, ask_groq
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import threading
from typing import Optional

# Load env variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# FastAPI setup
web_app = FastAPI(title="Antenhe Assistant API")

# Add CORS middleware
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for API requests
class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None

# API Endpoints
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
    """Endpoint for website queries"""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        answer = ask_groq(request.question)
        return {
            "status": "success",
            "answer": answer,
            "truncated": len(answer) >= 1024  # Indicate if response was truncated
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API ask error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question"
        )

def run_fastapi():
    """Run FastAPI server in production"""
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        web_app,
        host="0.0.0.0",
        port=port,
        log_config=None,
        access_log=False
    )

async def on_startup(app):
    """Telegram bot startup tasks"""
    await app.bot.set_my_commands([
        ("start", "Start the bot"),
        ("help", "Show help info"),
        ("projects", "Show Antenhe's projects"),
        ("ask", "Ask the AI about Antenhe Sileshi"),
    ])
    logger.info("Bot commands set up successfully")

def main():
    """Main application entry point"""
    # Start FastAPI server in a separate thread
    server_thread = threading.Thread(target=run_fastapi, daemon=True)
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

    logger.info("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()