import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import logging
import os
from dotenv import load_dotenv

# بارگذاری توکن ربات از فایل .env
load_dotenv()
TOKEN = "8068884649:AAFeNF1cV2orXyd9JZn8RyEPcZr8oW4lBAQ"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# اتصال به پایگاه داده SQLite
def create_connection():
    conn = sqlite3.connect('warehouse.db')
    return conn

# ایجاد جدول خرید در پایگاه داده
def create_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS purchases
                 (size TEXT, quantity INTEGER, price REAL)''')
    conn.commit()
    conn.close()

# دیکشنری برای نگهداری موجودی انبار برای هر سایز
main_warehouse = {}  # انبار اصلی (شامل سایزها)

# تابع شروع ربات
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("ثبت خرید جدید", callback_data='buy_new')],
        [InlineKeyboardButton("مشاهده موجودی انبار", callback_data='inventory')],
        [InlineKeyboardButton("ثبت فروش لاستیک", callback_data='sell')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! من ربات شما هستم. لطفاً گزینه‌ای را انتخاب کنید:", reply_markup=reply_markup)

# تابع نمایش موجودی انبار
async def inventory(update: Update, context):
    inventory_text = "موجودی انبارها:\n"
    if main_warehouse:
        for size, qty in main_warehouse.items():
            inventory_text += f"سایز {size}: {qty} لاستیک در انبار اصلی\n"
    else:
        inventory_text += "انبار اصلی خالی است.\n"
    await update.message.reply_text(inventory_text)

# تابع ثبت خرید جدید
async def buy_new(update: Update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("لطفاً سایز لاستیک را وارد کنید:")

# تابع دریافت سایز لاستیک
async def get_size(update: Update, context):
    size = update.message.text
    context.user_data['size'] = size
    await update.message.reply_text(f"شما سایز {size} را وارد کرده‌اید. حالا لطفاً قیمت لاستیک را وارد کنید:")

# تابع دریافت قیمت لاستیک
async def get_price(update: Update, context):
    try:
        price = float(update.message.text)
        size = context.user_data['size']  # سایز لاستیک
        context.user_data['price'] = price  # ذخیره قیمت لاستیک
        await update.message.reply_text(f"شما قیمت {price} را برای سایز {size} وارد کرده‌اید. حالا لطفاً تعداد لاستیک را وارد کنید:")
    except ValueError:
        await update.message.reply_text("لطفاً قیمت را به درستی وارد کنید.")

# تابع دریافت تعداد لاستیک
async def get_quantity(update: Update, context):
    try:
        quantity = int(update.message.text)
        size = context.user_data['size']  # سایز لاستیک
        price = context.user_data['price']  # قیمت لاستیک

        # ذخیره خرید در پایگاه داده
        conn = create_connection()
        c = conn.cursor()
        c.execute("INSERT INTO purchases (size, quantity, price) VALUES (?, ?, ?)", (size, quantity, price))
        conn.commit()
        conn.close()

        # افزودن لاستیک به انبار اصلی
        if size not in main_warehouse:
            main_warehouse[size] = 0
        main_warehouse[size] += quantity

        await update.message.reply_text(f"شما {quantity} لاستیک سایز {size} به قیمت {price} خریداری کردید. موجودی انبار اصلی به روز شد.")
    except ValueError:
        await update.message.reply_text("لطفاً تعداد لاستیک را به درستی وارد کنید.")

# تابع برای ثبت فروش لاستیک
async def sell(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("سایز 15", callback_data='sell_15')],
        [InlineKeyboardButton("سایز 16", callback_data='sell_16')],
        [InlineKeyboardButton("سایز 17", callback_data='sell_17')],
        [InlineKeyboardButton("بازگشت", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفاً سایز لاستیک مورد نظر برای فروش را انتخاب کنید:", reply_markup=reply_markup)

# تابع اصلی
def main():
    # ساخت پایگاه داده و جدول
    create_table()

    # ساخت اپلیکیشن با توکن ربات
    application = Application.builder().token(TOKEN).build()

    # تعریف دستورات ربات
    start_handler = CommandHandler("start", start)
    buy_new_handler = CommandHandler("buy_new", buy_new)
    sell_handler = CommandHandler("sell", sell)
    inventory_handler = CommandHandler("inventory", inventory)

    # افزودن دستورات به ربات
    application.add_handler(start_handler)
    application.add_handler(buy_new_handler)
    application.add_handler(sell_handler)
    application.add_handler(inventory_handler)

    # مدیریت دریافت سایز، قیمت و تعداد
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_size))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_price))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity))

    # اجرای ربات
    application.run_polling()

if __name__ == '__main__':
    main()