from typing import Final
import logging

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
    CallbackQueryHandler,
    Updater
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




if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    # app.add_handler(CommandHandler("start", start_command_handler))


    app.run_polling()