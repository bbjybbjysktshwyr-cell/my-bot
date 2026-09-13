import os
import asyncio
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في بوت دلتا! 🚀\n"
        "أرسل الأمر /generate لتوليد وحل الروابط تلقائياً."
    )

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("جاري تشغيل السكربت وتوليد الروابط، يرجى الانتظار...")
    
    try:
        # تشغيل ملف main.py مباشرة مع معامل توليد رابط واحد
        process = await asyncio.create_subprocess_exec(
            "python", "main.py", "--generate", "1",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        output_text = stdout.decode('utf-8')
        error_text = stderr.decode('utf-8')
        
        if process.returncode == 0:
            await msg.edit_text(f"تمت العملية بنجاح! 🎯\n\nالنتيجة:\n{output_text[-300:]}")
        else:
            await msg.edit_text(f"حدث خطأ أثناء التنفيد:\n{error_text[-300:]}")
            
    except Exception as e:
        await msg.edit_text(f"حدث استثناء: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate_command))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
