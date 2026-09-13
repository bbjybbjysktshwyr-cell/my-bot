import os
import asyncio
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    if "platorelay.com" in user_text or "d=" in user_text:
        # إرسال رسالة تنبيهية بأن العمل جارٍ
        status_msg = await update.message.reply_text("⏳ جاري حل الرابط واستخراج الكود، انتظر قليلاً...")
        
        try:
            # تشغيل main.py واستخراج النتيجة
            process = await asyncio.create_subprocess_exec(
                "python", "main.py", user_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            output_text = stdout.decode('utf-8')
            
            if process.returncode == 0:
                # إرسال الكود المستخرج كرسالة جديدة تماماً لتجنب مشاكل التعديل
                await update.message.reply_text(f"تم بنجاح! 🎯\n\n{output_text}")
            else:
                error_output = stderr.decode('utf-8') or output_text
                await update.message.reply_text(f"فشل في استخراج الكود:\n{error_output[-300:]}")
                
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ: {str(e)}")
    else:
        await update.message.reply_text("يرجى إرسال رابط دلتا صحيح.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
    print("Bot is running and waiting for links...")
    app.run_polling()

if __name__ == "__main__":
    main()
