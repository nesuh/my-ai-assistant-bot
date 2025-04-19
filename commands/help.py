from telegram import Update
from telegram.ext import ContextTypes
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👋 Hi {update.effective_user.first_name}, welcome to Antenhe's Portfolio Bot!")