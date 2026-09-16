import os
import asyncio
import subprocess
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

successful_requests_count = 1136
last_extracted_links = {}

def get_main_keyboard():
    keyboard = [
        ["🔗 تجاوز رابط دلتا أو الموقع الثاني"],
        ["🌐 المواقع المدعومة", "📖 شرح البوت"],
        [f"📊 الطلبات الناجحة: {successful_requests_count}"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك في بوت تجاوز الروابط (دلتا والمواقع الأخرى) 👋\n\nأرسل الرابط مباشرة وسأقوم باستخراجه:",
        reply_markup=get_main_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global successful_requests_count
    if not update.message or not update.message.text:
        return
        
    user_id = update.effective_user.id
    user_text = update.message.text.strip()
    
    if user_text in ["🔗 تجاوز رابط دلتا أو الموقع الثاني"]:
        await update.message.reply_text("أرسل رابط دلتا أو الرابط الثاني الآن:")
        return
    elif user_text in ["🌐 المواقع المدعومة"]:
        await update.message.reply_text("🌐 المواقع المدعومة:\n1. روابط موقع دلتا (عبر main.py)\n2. الموقع الثاني (عبر cli.py)")
        return
    elif user_text in ["📖 شرح البوت"]:
        await update.message.reply_text("فقط قم بإرسال الرابط وسيقوم البوت باختيار الأداة المناسبة لتجاوزه تلقائياً.")
        return
    elif "الطلبات الناجحة" in user_text:
        await update.message.reply_text(f"📊 عدد الطلبات الناجحة حتى الآن: {successful_requests_count}")
        return

    if "http://" in user_text or "https://" in user_text:
        status_msg = await update.message.reply_text("⏳ جارٍ فحص ومعالجة الرابط عبر الأداة المخصصة...")
        
        extracted_result = ""
        try:
            # التحقق مما إذا كان الرابط يخص دلتا أو الموقع الثاني
            if "platorelay" in user_text.lower() or "delta" in user_text.lower():
                process = await asyncio.create_subprocess_exec(
                    "python3", "main.py", user_text,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # تشغيل الموقع الثاني بطريقة صحيحة كموديول لتجنب خطأ الـ Import
                process = await asyncio.create_subprocess_exec(
                    "python3", "-m", "cli", user_text,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            output_text = stdout.decode('utf-8', errors='ignore').strip()
            error_text = stderr.decode('utf-8', errors='ignore').strip()
            
            if output_text:
                extracted_result = output_text
            elif error_text:
                extracted_result = error_text
            else:
                extracted_result = "لم يتم إرجاع أي نتيجة من الأداة."
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

        if extracted_result and "❌" not in extracted_result and "Traceback" not in extracted_result and "لم يتم" not in extracted_result:
            successful_requests_count += 1
            last_extracted_links[user_id] = extracted_result
            result_message = f"✅ **النتيجة المستخرجة:**\n`{extracted_result}`"
            keyboard = [[InlineKeyboardButton("📋 نسخ النتيجة", callback_data="copy_result")]]
            await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(extracted_result)
    else:
        await update.message.reply_text("يرجى إرسال رابط صحيح يبدأ بـ http:// أو https://.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    try:
        await query.answer("تم النسخ بنجاح!", show_alert=True)
    except:
        pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running perfectly...")
    app.run_polling()

if __name__ == "__main__":
    main()
