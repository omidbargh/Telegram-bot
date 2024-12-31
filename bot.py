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

# متغیرها برای ذخیره موجودی انبار
main_warehouse = {"tire": 100}  # انبار اصلی
temporary_warehouse = {"tire": 0}  # انبار موقت
sales_profit = 0  # متغیر ذخیره سود حاصل از فروش

# تابع شروع ربات
async def start(update: Update, context):
    await update.message.reply_text("سلام! من ربات شما هستم. دستورات موجود: /start, /inventory, /buy, /sell, /transfer")

# تابع نمایش موجودی انبارها
async def inventory(update: Update, context):
    main_warehouse_status = f"موجودی انبار اصلی: {main_warehouse['tire']} لاستیک"
    temporary_warehouse_status = f"موجودی انبار موقت: {temporary_warehouse['tire']} لاستیک"
    await update.message.reply_text(f"{main_warehouse_status}\n{temporary_warehouse_status}")

# تابع ثبت خرید
async def buy(update: Update, context):
    try:
        quantity = int(context.args[0])  # تعداد لاستیک از آرگومان دستور
        main_warehouse['tire'] += quantity
        await update.message.reply_text(f"شما {quantity} لاستیک خریدید. موجودی جدید انبار اصلی: {main_warehouse['tire']} لاستیک")
    except (IndexError, ValueError):
        await update.message.reply_text("لطفاً تعداد خرید را وارد کنید. مثلا: /buy 10")

# تابع ثبت فروش
async def sell(update: Update, context):
    try:
        quantity = int(context.args[0])  # تعداد لاستیک از آرگومان دستور
        if temporary_warehouse['tire'] >= quantity:
            temporary_warehouse['tire'] -= quantity
            profit = quantity * 100  # فرض می‌کنیم سود هر لاستیک 100 تومان است
            global sales_profit
            sales_profit += profit
            await update.message.reply_text(f"شما {quantity} لاستیک فروختید. سود شما: {profit} تومان. موجودی جدید انبار موقت: {temporary_warehouse['tire']} لاستیک")
        else:
            await update.message.reply_text(f"موجودی کافی نیست! موجودی فعلی انبار موقت: {temporary_warehouse['tire']} لاستیک")
    except (IndexError, ValueError):
        await update.message.reply_text("لطفاً تعداد فروش را وارد کنید. مثلا: /sell 5")

# تابع انتقال لاستیک از انبار اصلی به انبار موقت
async def transfer(update: Update, context):
    try:
        quantity = int(context.args[0])  # تعداد لاستیک از آرگومان دستور
        if main_warehouse['tire'] >= quantity:
            main_warehouse['tire'] -= quantity
            temporary_warehouse['tire'] += quantity
            await update.message.reply_text(f"شما {quantity} لاستیک از انبار اصلی به انبار موقت منتقل کردید.")
        else:
            await update.message.reply_text(f"موجودی کافی نیست! موجودی فعلی انبار اصلی: {main_warehouse['tire']} لاستیک")
    except (IndexError, ValueError):
        await update.message.reply_text("لطفاً تعداد انتقال را وارد کنید. مثلا: /transfer 10")

# تابع نمایش سود
async def profit(update: Update, context):
    await update.message.reply_text(f"سود کل فروش شما: {sales_profit} تومان")

# تنظیمات ربات و دستورات
def main():
    # ساخت اپلیکیشن با توکن ربات
    application = Application.builder().token(TOKEN).build()

    # تعریف دستورات ربات
    start_handler = CommandHandler("start", start)
    inventory_handler = CommandHandler("inventory", inventory)
    buy_handler = CommandHandler("buy", buy)
    sell_handler = CommandHandler("sell", sell)
    transfer_handler = CommandHandler("transfer", transfer)
    profit_handler = CommandHandler("profit", profit)

    # اضافه کردن دستورات به ربات
    application.add_handler(start_handler)
    application.add_handler(inventory_handler)
    application.add_handler(buy_handler)
    application.add_handler(sell_handler)
    application.add_handler(transfer_handler)
    application.add_handler(profit_handler)

    application.run_polling()

if __name__ == '__main__':
    main()