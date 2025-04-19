from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from utils.project_data import projects

#     query = update.callback_query
#     await query.answer()

#     title = query.data
#     for project in projects:
#         if project["title"] == title:
#             description = project["description"]
#             await query.edit_message_text(f"🔹 *{title}*\n\n{description}", parse_mode="Markdown")
#             break
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    keyboard = [
        [InlineKeyboardButton(project['title'], callback_data=project['title'])] for project in projects
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    

    await update.message.reply_text('📂 Select a project to learn more:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
 
    project_title = query.data
    
    # Find the project description based on title
    project = next(p for p in projects if p['title'] == project_title)
    
    # Send project description as a message
    await query.answer()  # Acknowledge the click
    await query.edit_message_text(f"🔹 {project['title']} - {project['description']}")