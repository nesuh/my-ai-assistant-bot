import json
import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Updated load_portfolio_data() function
def load_portfolio_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        utils_dir = os.path.join(current_dir, "..", "utils")  
        file_path = os.path.join(utils_dir, "history.json")
        
        print(f"DEBUG: Attempting to load from {file_path}")  
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")
            
        with open(file_path, "r") as f:
            data = json.load(f)
            print("DEBUG: Successfully loaded portfolio data")  # Debug print
            return data
            
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in history.json: {e}")
        raise
    except Exception as e:
        print(f"ERROR loading portfolio data: {e}")
        raise


try:
    portfolio_data = load_portfolio_data() 
except FileNotFoundError as e:
    print(f"Error: {e}")
    portfolio_data = None  

def ask_groq(user_question: str) -> str:
    if portfolio_data is None:
        return "⚠️ Portfolio data could not be loaded."

    payload = {
        'model': 'llama-3.3-70b-versatile',
        'messages': [
            {'role': 'system', 'content': portfolio_data['intro']},
            {'role': 'system', 'content': portfolio_data['note']},
            {'role': 'system', 'content': portfolio_data['instruction']},
            {'role': 'system', 'content': json.dumps(portfolio_data['facts'])},
            {'role': 'user', 'content': user_question}
        ],
        'temperature': 0.0,
        'top_p': 1.0,
        'max_tokens': 512
    }
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

# Telegram command handler for /ask
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = ' '.join(context.args)
    if not user_question:
        await update.message.reply_text("❓ Please ask something after /ask.")
        return

    # Inform user processing
    await update.message.reply_text("🤔 Let me think...")

    try:
        answer = ask_groq(user_question)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Sorry, something went wrong: {e}")
