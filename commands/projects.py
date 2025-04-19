from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from utils.project_data import projects

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display all projects as inline buttons"""
    # Create two columns for better mobile display
    keyboard = [
        [InlineKeyboardButton(project['title'], callback_data=f"project_{i}")]
        for i, project in enumerate(projects)
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        '📂 *Select a project to view details:*',
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle project selection callback"""
    query = update.callback_query
    await query.answer()
    
    # Extract project index from callback_data
    project_index = int(query.data.split("_")[1])
    project = projects[project_index]
    
    # Format detailed response
    response = (
        f"🔹 *{project['title']}*\n\n"
        f"📝 *Description:* {project['description']}\n\n"
        f"🛠️ *Technologies:* {', '.join(project['technologies'])}\n\n"
        f"✨ *Key Features:*\n- " + "\n- ".join(project['features'])
    )
    
    # Add back button
    keyboard = [[InlineKeyboardButton("◀️ Back to Projects", callback_data="back_to_projects")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        response,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button callback"""
    query = update.callback_query
    await query.answer()
    await handle(update, context)  # Reuse the initial handler

# Register handlers
def setup_handlers(application):
    application.add_handler(CallbackQueryHandler(button, pattern=r"^project_\d+$"))
    application.add_handler(CallbackQueryHandler(back_handler, pattern=r"^back_to_projects$"))