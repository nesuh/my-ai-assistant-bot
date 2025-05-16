import json
import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes
from typing import Optional, Dict, Any
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama3-70b-8192"
MAX_TOKENS = 1024
TIMEOUT = 15  # seconds

def load_portfolio_data() -> Optional[Dict[str, Any]]:
    """Load portfolio data from JSON file with multiple fallback paths"""
    possible_paths = [
        os.path.join("utils", "history.json"),
        os.path.join(os.path.dirname(__file__), "..", "utils", "history.json"),
        os.path.join(os.getcwd(), "utils", "history.json"),
        "/app/utils/history.json"  # For container deployments
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded portfolio data from {path}")
                    return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load from {path}: {str(e)}")
            continue
    
    logger.error("Could not load portfolio data from any path")
    return None

# Load portfolio data at module level
portfolio_data = load_portfolio_data()

def generate_payload(user_question: str) -> Dict[str, Any]:
    """Generate the payload for Groq API"""
    if not portfolio_data:
        raise ValueError("Portfolio data not available")
    
    return {
        'model': DEFAULT_MODEL,
        'messages': [
            {'role': 'system', 'content': portfolio_data.get('intro', '')},
            {'role': 'system', 'content': portfolio_data.get('note', '')},
            {'role': 'system', 'content': portfolio_data.get('instruction', '')},
            {'role': 'system', 'content': json.dumps(portfolio_data.get('facts', {}))},
            {'role': 'user', 'content': user_question}
        ],
        'temperature': 0.3,
        'top_p': 0.9,
        'max_tokens': MAX_TOKENS,
        'stream': False
    }

def ask_groq(user_question: str) -> str:
    """Query Groq API with comprehensive error handling"""
    if not user_question.strip():
        return "Please provide a valid question."
    
    if not portfolio_data:
        logger.error("Portfolio data not loaded")
        return "I'm currently unable to access my knowledge base. Please try again later."

    try:
        payload = generate_payload(user_question)
        headers = {
            'Authorization': f'Bearer {GROQ_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
        
    except requests.exceptions.Timeout:
        logger.error("Groq API request timed out")
        return "The request timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        logger.error(f"Groq API request failed: {str(e)}")
        return "I'm having trouble connecting to the AI service. Please try again later."
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected response format: {str(e)}")
        return "I received an unexpected response format from the AI service."
    except Exception as e:
        logger.error(f"Unexpected error in ask_groq: {str(e)}", exc_info=True)
        return "An unexpected error occurred while processing your question."

# Telegram command handler for /ask
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ask command from Telegram"""
    user_question = ' '.join(context.args)
    if not user_question:
        await update.message.reply_text("❓ Please ask something after /ask.")
        return

    await update.message.reply_text("🤔 Let me think...")

    try:
        answer = ask_groq(user_question)
        await update.message.reply_text(answer)
    except Exception as e:
        logger.error(f"Error in Telegram /ask: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Sorry, something went wrong. Please try again later.")