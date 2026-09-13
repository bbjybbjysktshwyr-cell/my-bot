import os
import asyncio
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # التحقق من أن النص المدخل هو رابط دلتا أو يحتوي على تكت
    if "platorelay.com" in user_text or "d=" in user_text:
        msg = await update.message.reply_text("⏳ جاري معالجة الرابط واستخراج الكود عبر الأداة، يرجى الانتظار...")
        
        try:
            # تشغيل main.py مع الرابط الذي أرسلته
            process = await asyncio.create_subprocess_exec(
                "python", "main.py", user_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            output_text = stdout.decode('utf-8')
            
            if process.returncode == 0 and "DELTA KEY" in output_text:
                # استخراج الكود من مخرجات الأداة وإرساله
                await msg.edit_text(f"تم بنجاح! 🎯\n\n{output_text}")
            else:
                await msg.edit_text(f"فشل في استخراج الكود:\n{output_text[-400:]}")
                
        except Exception as e:
            await msg.edit_text(f"حدث خطأ: {str(e)}")
    else:
        await update.message.reply_text("يرجى إرسال رابط دلتا صحيح لكي أستخرج لك الكود.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # الاستماع لأي رسالة نصية تحتوي على رابط وإرسالها للمعالجة
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
    
    print("Bot is running and waiting for links...")
    app.run_polling()

if __name__ == "__main__":
    main()
