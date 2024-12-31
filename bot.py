import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
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

# ایجاد جدول‌ها در پایگاه داده
def create_tables():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS purchases (size TEXT, quantity INTEGER, price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS main_inventory (size TEXT, quantity INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS temp_inventory (size TEXT, quantity INTEGER)''')
    conn.commit()
    conn.close()

# تابع شروع ربات
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("ثبت خرید جدید", callback_data='buy_new')],
        [InlineKeyboardButton("مشاهده موجودی انبار اصلی", callback_data='main_inventory')],
        [InlineKeyboardButton("مشاهده موجودی انبار موقت", callback_data='temp_inventory')],
        [InlineKeyboardButton("انتقال به انبار موقت", callback_data='transfer')],
        [InlineKeyboardButton("ثبت فروش لاستیک", callback_data='sell')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! من ربات شما هستم. لطفاً گزینه‌ای را انتخاب کنید:", reply_markup=reply_markup)

# نمایش موجودی انبار اصلی
async def main_inventory(update: Update, context):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM main_inventory')
    rows = c.fetchall()
    conn.close()

    if rows:
        inventory_text = "موجودی انبار اصلی:\n"
        for row in rows:
            inventory_text += f"سایز: {row[0]} - تعداد: {row[1]}\n"
    else:
        inventory_text = "موجودی انبار اصلی خالی است."
    
    await update.message.reply_text(inventory_text)

# نمایش موجودی انبار موقت
async def temp_inventory(update: Update, context):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM temp_inventory')
    rows = c.fetchall()
    conn.close()

    if rows:
        inventory_text = "موجودی انبار موقت:\n"
        for row in rows:
            inventory_text += f"سایز: {row[0]} - تعداد: {row[1]}\n"
    else:
        inventory_text = "موجودی انبار موقت خالی است."
    
    await update.message.reply_text(inventory_text)

# تابع ثبت خرید جدید
async def buy_new(update: Update, context):
    await update.callback_query.answer()  # ضروری برای جلوگیری از "loading"
    await update.callback_query.edit_message_text("لطفاً سایز لاستیک را وارد کنید:")

# دریافت سایز لاستیک
async def get_size(update: Update, context):
    size = update.message.text
    context.user_data['size'] = size
    await update.message.reply_text(f"شما سایز {size} را وارد کرده‌اید. حالا لطفاً قیمت لاستیک را وارد کنید:")

# دریافت قیمت لاستیک
async def get_price(update: Update, context):
    try:
        price = float(update.message.text)
        size = context.user_data['size']
        context.user_data['price'] = price
        await update.message.reply_text(f"شما قیمت {price} را برای سایز {size} وارد کرده‌اید. حالا لطفاً تعداد لاستیک را وارد کنید:")
    except ValueError:
        await update.message.reply_text("لطفاً قیمت را به درستی وارد کنید.")

# دریافت تعداد لاستیک
async def get_quantity(update: Update, context):
    try:
        quantity = int(update.message.text)
        size = context.user_data['size']
        price = context.user_data['price']

        # ذخیره خرید در پایگاه داده
        conn = create_connection()
        c = conn.cursor()
        c.execute("INSERT INTO purchases (size, quantity, price) VALUES (?, ?, ?)", (size, quantity, price))
        conn.commit()

        # افزودن لاستیک به انبار اصلی
        c.execute('SELECT * FROM main_inventory WHERE size = ?', (size,))
        row = c.fetchone()
        if row:
            new_quantity = row[1] + quantity
            c.execute('UPDATE main_inventory SET quantity = ? WHERE size = ?', (new_quantity, size))
        else:
            c.execute('INSERT INTO main_inventory (size, quantity) VALUES (?, ?)', (size, quantity))
        conn.commit()
        conn.close()

        await update.message.reply_text(f"شما {quantity} لاستیک سایز {size} به قیمت {price} خریداری کردید. موجودی انبار اصلی به روز شد.")
    except ValueError:
        await update.message.reply_text("لطفاً تعداد لاستیک را به درستی وارد کنید.")

# تابع انتقال لاستیک از انبار اصلی به انبار موقت
async def transfer(update: Update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("لطفاً سایز لاستیک را برای انتقال از انبار اصلی به انبار موقت وارد کنید:")

# دریافت سایز برای انتقال
async def transfer_size(update: Update, context):
    size = update.message.text
    context.user_data['transfer_size'] = size
    await update.message.reply_text(f"شما سایز {size} را برای انتقال انتخاب کرده‌اید. حالا لطفاً تعداد را وارد کنید:")

# دریافت تعداد لاستیک برای انتقال
async def transfer_quantity(update: Update, context):
    try:
        quantity = int(update.message.text)
        size = context.user_data['transfer_size']

        conn = create_connection()
        c = conn.cursor()

        # بررسی موجودی انبار اصلی
        c.execute('SELECT * FROM main_inventory WHERE size = ?', (size,))
        row = c.fetchone()
        if row and row[1] >= quantity:
            # انتقال از انبار اصلی به انبار موقت
            c.execute('SELECT * FROM temp_inventory WHERE size = ?', (size,))
            temp_row = c.fetchone()
            if temp_row:
                new_temp_quantity = temp_row[1] + quantity
                c.execute('UPDATE temp_inventory SET quantity = ? WHERE size = ?', (new_temp_quantity, size))
            else:
                c.execute('INSERT INTO temp_inventory (size, quantity) VALUES (?, ?)', (size, quantity))

            new_main_quantity = row[1] - quantity
            c.execute('UPDATE main_inventory SET quantity = ? WHERE size = ?', (new_main_quantity, size))

            conn.commit()
            conn.close()

            await update.message.reply_text(f"{quantity} لاستیک سایز {size} از انبار اصلی به انبار موقت منتقل شد.")
        else:
            await update.message.reply_text(f"موجودی کافی برای انتقال از انبار اصلی به انبار موقت وجود ندارد.")
    except ValueError:
        await update.message.reply_text("لطفاً تعداد را به درستی وارد کنید.")

# تابع فروش لاستیک از انبار موقت
async def sell(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("سایز 15", callback_data='sell_15')],
        [InlineKeyboardButton("سایز 16", callback_data='sell_16')],
        [InlineKeyboardButton("سایز 17", callback_data='sell_17')],
        [InlineKeyboardButton("بازگشت", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفاً سایز لاستیک مورد نظر برای فروش را انتخاب کنید:", reply_markup=reply_markup)

# تابع مدیریت callback ها
async def button(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "buy_new":
        await buy_new(update, context)
    elif query.data == "main_inventory":
        await main_inventory(update, context)
    elif query.data == "temp_inventory":
        await temp_inventory(update, context)
    elif query.data == "transfer":
        await transfer(update, context)
    elif query.data.startswith("sell_"):
        size = query.data.split('_')[1]
        # روند فروش را پیاده‌سازی کنید
        await query.edit_message_text(f"شما سایز {size} را برای فروش انتخاب کردید. لطفاً تعداد مورد نظر را وارد کنید:")

# تابع اصلی
def main():
    # ساخت پایگاه داده و جدول‌ها
    create_tables()

    # ساخت اپلیکیشن با توکن ربات
    application = Application.builder().token(TOKEN).build()

    # تعریف دستورات ربات
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    # مدیریت CallbackQuery
    application.add_handler(CallbackQueryHandler(button))

    # مدیریت دریافت سایز، قیمت و تعداد
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_size))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_price))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, transfer_size))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, transfer_quantity))

    # اجرای ربات
    application.run_polling()

if __name__ == '__main__':
    main()