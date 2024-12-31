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

# دیکشنری برای نگهداری موجودی انبار برای هر سایز
main_warehouse = {}  # انبار اصلی (شامل سایزها)
temporary_warehouse = {}  # انبار موقت

# تابع شروع ربات
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("خرید لاستیک", callback_data='buy')],
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
    
    if temporary_warehouse:
        for size, qty in temporary_warehouse.items():
            inventory_text += f"سایز {size}: {qty} لاستیک در انبار موقت\n"
    else:
        inventory_text += "انبار موقت خالی است.\n"
    
    await update.message.reply_text(inventory_text)

# تابع برای خرید لاستیک
async def buy(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("سایز 15", callback_data='buy_15')],
        [InlineKeyboardButton("سایز 16", callback_data='buy_16')],
        [InlineKeyboardButton("سایز 17", callback_data='buy_17')],
        [InlineKeyboardButton("بازگشت", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفاً سایز لاستیک مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)

# تابع برای ثبت خرید پس از انتخاب سایز
async def handle_buy_size(update: Update, context):
    query = update.callback_query
    size = query.data.split('_')[1]  # سایز انتخاب شده
    query.answer()  # پاسخ به درخواست callback

    # دریافت تعداد لاستیک از کاربر
    await query.edit_message_text(f"شما سایز {size} را انتخاب کرده‌اید. لطفاً تعداد لاستیک مورد نظر را وارد کنید:")

    # ذخیره سایز انتخاب شده برای استفاده بعدی
    context.user_data['size'] = size

# تابع برای دریافت تعداد لاستیک
async def get_quantity(update: Update, context):
    try:
        quantity = int(update.message.text)
        size = context.user_data['size']  # سایز ذخیره‌شده

        # افزودن لاستیک به انبار اصلی
        if size not in main_warehouse:
            main_warehouse[size] = 0
        main_warehouse[size] += quantity

        await update.message.reply_text(f"شما {quantity} لاستیک سایز {size} خریداری کردید. موجودی انبار اصلی به روز شد.")
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

# تابع برای ثبت فروش پس از انتخاب سایز
async def handle_sell_size(update: Update, context):
    query = update.callback_query
    size = query.data.split('_')[1]  # سایز انتخاب شده
    query.answer()  # پاسخ به درخواست callback

    # دریافت تعداد لاستیک از کاربر
    await query.edit_message_text(f"شما سایز {size} را انتخاب کرده‌اید. لطفاً تعداد لاستیک مورد نظر برای فروش را وارد کنید:")

    # ذخیره سایز انتخاب شده برای استفاده بعدی
    context.user_data['size'] = size

# تابع اصلی
def main():
    # ساخت اپلیکیشن با توکن ربات
    application = Application.builder().token(TOKEN).build()

    # تعریف دستورات ربات
    start_handler = CommandHandler("start", start)
    buy_handler = CommandHandler("buy", buy)
    sell_handler = CommandHandler("sell", sell)
    inventory_handler = CommandHandler("inventory", inventory)

    # افزودن دستورات به ربات
    application.add_handler(start_handler)
    application.add_handler(buy_handler)
    application.add_handler(sell_handler)
    application.add_handler(inventory_handler)

    # مدیریت انتخاب سایز خرید و فروش
    application.add_handler(CallbackQueryHandler(handle_buy_size, pattern='^buy_'))
    application.add_handler(CallbackQueryHandler(handle_sell_size, pattern='^sell_'))

    # مدیریت دریافت تعداد لاستیک
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity))

    # اجرای ربات
    application.run_polling()

if __name__ == '__main__':
    main()
    