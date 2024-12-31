from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
import logging
import os
from dotenv import load_dotenv

# بارگذاری توکن ربات از فایل .env
load_dotenv()
TOKEN = "8068884649:AAFeNF1cV2orXyd9JZn8RyEPcZr8oW4lBAQ"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# تابع شروع ربات
async def start(update: Update, context):
    await update.message.reply_text("سلام! من ربات شما هستم.")

# تنظیمات ربات و دستورات
def main():
    # ساخت اپلیکیشن با توکن ربات
    application = Application.builder().token(TOKEN).build()

    # تعریف دستورات ربات
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    application.run_polling()

if __name__ == '__main__':
    main()