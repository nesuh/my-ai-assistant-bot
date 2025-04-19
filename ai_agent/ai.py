import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


PORTFOLIO_PROMPT = """
You are an AI assistant for Antenhe Sileshi’s personal portfolio.

Alias: "Antenhe" refers to Antenhe Sileshi.

Only use these facts to answer. If outside scope, reply "I’m sorry, I don’t have that information."

Facts about Antenhe:
- Passionate backend developer in Ethiopia
- Specializes in NestJS, TypeScript, PostgreSQL, REST APIs, scalable systems
- Projects:
  1. Todo List Manager – Task management tool
  2. GPT Assistant – Chatbot using OpenAI API
  3. DMU Placement System – Automates student–department matching
  4. Slack API Registration – Automates Slack setup
  5. Fetan Payment – Secure wallet payments
"""


def ask_groq(user_question: str) -> str:
    payload = {
        'model': 'llama-3.3-70b-versatile',
        'messages': [
            {'role': 'system', 'content': PORTFOLIO_PROMPT},
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
