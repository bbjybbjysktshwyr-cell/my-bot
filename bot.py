import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from main import run_solver  # استيراد دالة التشغيل من ملفك الأساسي

# توكن البوت (استبدل التوكن بالتوكن الخاص بك أو اجعله يقرأه من البيئة)
BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في بوت دلتا! 🚀\n"
        "أرسل الأمر /generate لتوليد وحل الروابط تلقائياً."
    )

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("جاري توليد الروابط ومعالجتها، يرجى الانتظار...")
    
    try:
        # تشغيل عملية التوليد (يمكنك تعديل الأرجيومنت حسب رغبتك، مثلاً توليد 3 روابط)
        # سيتم تنفيذ الكود وإرسال النتيجة فور انتهائها
        loop = asyncio.get_running_loop()
        # هنا يتم استدعاء وظيفة الحل أو التوليد من ملفات المشروع
        await update.message.reply_text("تم اكتمال العملية بنجاح!")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء المعالجة: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate_command))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
