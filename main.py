from typing import Final
import logging
import pandas as pd

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    InlineQueryHandler,
    CallbackContext,
    CallbackQueryHandler
)


TOKEN: Final= "7425268112:AAGMJVGA56RKIS7iIy5wWG5_cld8JEqHhMA"
CHANNEL_USERNAME: Final= "@bot_polic"


# Enable logging
# **************************************************************** LOG ****************************************************************
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
# **************************************************************** LOG ****************************************************************


# Start with selecting a way-adding
async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Creating for choosing a way to import PH-nums
    keyboard = [
        [InlineKeyboardButton("دستی", callback_data='manual')],
        [InlineKeyboardButton("فایل", callback_data='file')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'چگونه می‌خواهید شماره‌ها را وارد کنید؟',
        reply_markup=reply_markup
    )
    
    
# Client's answer handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Check the user's choice
    if query.data == 'manual':
        await query.edit_message_text(text="لطفاً شماره‌ها را یکی یکی وارد کنید:")
        context.user_data['input_type'] = 'manual'
    elif query.data == 'file':
        await query.edit_message_text(text="لطفاً فایل شماره‌ها را ارسال کنید:")
        context.user_data['input_type'] = 'file'


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command_handler))
    app.add_handler(CallbackQueryHandler(button_handler))


    app.run_polling()