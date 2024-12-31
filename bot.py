from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = "8068884649:AAFeNF1cV2orXyd9JZn8RyEPcZr8oW4lBAQ"  # توکن شما

updater = Updater(TOKEN)
dispatcher = updater.dispatcher

def start(update, context):
    update.message.reply_text('سلام! من ربات شما هستم.')

def help(update, context):
    update.message.reply_text('دستورات من: /start, /help, /buy, /sell')

def buy(update, context):
    update.message.reply_text('دستور خرید ثبت شد.')

def sell(update, context):
    update.message.reply_text('دستور فروش ثبت شد.')

def inventory(update, context):
    update.message.reply_text('موجودی انبار: ...')

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('buy', buy))
dispatcher.add_handler(CommandHandler('sell', sell))
dispatcher.add_handler(CommandHandler('inventory', inventory))

updater.start_polling()
updater.idle()