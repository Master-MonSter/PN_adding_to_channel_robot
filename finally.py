from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import InputPhoneContact
import os
import re

BOT_TOKEN = 'YOUR_BOT_TOKEN'
API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
PHONE_NUMBER = 'YOUR_PHONE_NUMBER'  # Account number
CHANNEL_USERNAME = 'CHANNEL_USERNAME'

# Creating a telethon connection
client = TelegramClient('session_name', API_ID, API_HASH)

report = []
success_count = 0
fail_count = 0

# Checking for valid phone number
def check_phone_number_validation(phone_number: str):
    pattern = r"^(0|0098|\+98)9(0[1-5]|[13]\d|2[0-2]|9[0-4]|98)\d{7}$"

    # Example of usage:
    match = re.match(pattern, phone_number)
    if match:
        return True
    else:
        return False
      

# Creating 2btns to prepare for sending phone numbers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Creating for choosing a way to import PH-nums
    keyboard = [
        [InlineKeyboardButton("ورود دستی", callback_data='manual')],
        [InlineKeyboardButton("ارسال فایل", callback_data='file')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'چگونه می‌خواهید شماره‌ها را وارد کنید؟',
        reply_markup=reply_markup
    )

# Processing client query
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Check the user's choice
    if query.data == 'manual':
        await query.edit_message_text(text="لطفاً شماره‌ها را به فرمت زیر وارد کنید:\nتکی:\nبه فرمت 9123334444 (0 ,0098, 98+) \n\nچندتایی:\n شماره ها را با علامت , از یکدیگر جدا کنید: 09152223333,09154445555 ")
        context.user_data['input_type'] = 'manual'
    elif query.data == 'file':
        await query.edit_message_text(text="لطفاً فایل حاوی شماره‌ها (فرمت CSV) را ارسال کنید:")
        context.user_data['input_type'] = 'file'

# Adding manuall number to entered
async def manual_number_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global fail_count, success_count, report
    
    if context.user_data.get('input_type') == 'manual':
        # Processing numbers
        phone_numbers = update.message.text
        print(phone_numbers)
        
        if len((phone_numbers.split(","))) > 1:
            # Remove whitespace and Separate numbers 
            phone_numbers = [num.replace(" ","") for num in phone_numbers.split(",")]
            phone_numbers = [num for num in phone_numbers if num]
            print(phone_numbers)
        else:
            phone_numbers = list(phone_numbers)

        # Using telethon for adding numbers to channel
        for phone_number in phone_numbers:
            if check_phone_number_validation(phone_number):
                await add_number_to_channel(phone_number)
        text = f"Success count: {success_count}\nError count: {fail_count}\nReports: {report}"    
        await context
                

# Getting file and processing it
async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('input_type') == 'file':
        file = update.message.document
        # Saving file
        file_path = await file.get_file().download()
        await update.message.reply_text('فایل دریافت شد و در حال پردازش است.')

        # Openning file and use it
        with open(file_path, 'r') as f:
            phone_numbers = [line.strip() for line in f.readlines()]

        # Adding to channel
        for phone_number in phone_numbers:
            if check_phone_number_validation(phone_number):
                await add_number_to_channel(phone_number)

        # Deleting file after use it 
        os.remove(file_path)
        await update.message.reply_text('شماره‌ها با موفقیت پردازش شدند.')

# Using telethon for adding to channel
async def add_number_to_channel(phone_number: str) -> None:
    global fail_count, success_count, report
    
    async with client:
        await client.start(PHONE_NUMBER)
        try:
            # Adding to contact
            contact = InputPhoneContact(client_id=0, phone=phone_number, first_name="Temp", last_name="")
            result = await client(ImportContactsRequest([contact]))

            # If there is a Telegram user's phone number, we will add it to the channel
            if result.users:
                user_id = result.users[0].id
                channel = await client.get_entity(CHANNEL_USERNAME)
                await client(InviteToChannelRequest(channel, [user_id]))
                success_count += 1
                report.append(f'User with {phone_number} added successfully!')
                print(f'User with {phone_number} added successfully!')
            else:
                fail_count += 1
                report.append(f'User with {phone_number} does not have a Telegram account.')
                print(f'User with {phone_number} does not have a Telegram account.')
        except Exception as e:
            fail_count += 1
            report.append(f'Error while adding {phone_number}: {str(e)}')
            print(f'Error while adding {phone_number}: {str(e)}')


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manual_number_entry))
    app.add_handler(MessageHandler(filters.Document.ALL, file_handler))

    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
