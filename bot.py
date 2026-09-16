import os
import asyncio
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك. أرسل رابط دلتا مباشرة وسأقوم باستخراج النتيجة لك فوراً وبدون أزرار.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_text = update.message.text.strip()

    if "http://" in user_text or "https://" in user_text:
        status_msg = await update.message.reply_text("⏳ جارٍ معالجة رابط دلتا...")
        
        extracted_result = ""
        try:
            # تشغيل ملف main.py الخاص بدلتا مع الرابط المرسل
            process = await asyncio.create_subprocess_exec(
                "python3", "main.py", user_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=40)
            output_text = stdout.decode('utf-8', errors='ignore').strip()
            error_text = stderr.decode('utf-8', errors='ignore').strip()
            
            if output_text:
                extracted_result = output_text
            elif error_text:
                extracted_result = error_text
            else:
                extracted_result = "لم يتم إرجاع أي نتيجة."
        except asyncio.TimeoutError:
            try:
                process.kill()
            except:
                pass
            extracted_result = "❌ انتهت مهلة الانتظار (Timeout)."
        except Exception as e:
            extracted_result = f"❌ حدث خطأ: {e}"
            
        try:
            await status_msg.delete()
        except:
            pass

        # إرسال النتيجة الصافية بدون أزرار
        await update.message.reply_text(extracted_result)
    else:
        await update.message.reply_text("يرجى إرسال رابط دلتا صحيح يبدأ بـ http:// أو https://.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Delta Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
