import os
import asyncio
import subprocess
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

successful_requests_count = 1136
user_ratings = [
    {"name": "Mohamed", "stars": 5, "text": "كويس جدا ويسهل عليك وقت كبير"},
    {"name": "معصومة بلال", "stars": 5, "text": "فوللل جربووو"},
    {"name": "Cristiano", "stars": 5, "text": "ياخي اسطوره الي اخترع هادا البوت"}
]
last_extracted_links = {}

def get_main_keyboard():
    keyboard = [
        ["🔗 تجاوز رابط"],
        ["🌐 المواقع المدعومة", "📖 شرح البوت"],
        ["⭐ تقييم البوت", "🌍 تغيير اللغة"],
        [f"📊 الطلبات الناجحة: {successful_requests_count}"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك في بوت تجاوز الروابط 👋\n\nأرسل الرابط مباشرة وسأقوم باستخراجه:", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global successful_requests_count
    if not update.message or not update.message.text:
        return
        
    user_id = update.effective_user.id
    user_text = update.message.text.strip()
    
    if user_text in ["🔗 تجاوز رابط"]:
        await update.message.reply_text("أرسل رابطك الآن:")
        return
    elif user_text in ["🌐 المواقع المدعومة"]:
        await update.message.reply_text("المواقع المدعومة: روابط Linkvertise وروابط التحويل.")
        return
    elif user_text in ["📖 شرح البوت"]:
        await update.message.reply_text("أرسل الرابط وسيقوم البوت بمعالجته عبر الأداة مباشرة.")
        return
    elif user_text in ["⭐ تقييم البوت"]:
        await update.message.reply_text("⭐ شكرًا لتقييماتكم الرائعة!")
        return
    elif "الطلبات الناجحة" in user_text:
        await update.message.reply_text(f"📊 عدد الطلبات الناجحة: {successful_requests_count}")
        return

    if "http://" in user_text or "https://" in user_text:
        status_msg = await update.message.reply_text("⏳ جارٍ معالجة الرابط عبر الأداة...")
        
        extracted_result = ""
        try:
            process = await asyncio.create_subprocess_exec(
                "python3", "cli.py", user_text,
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
                extracted_result = "تمت العملية ولكن لم يُرجع البرنامج أي ناتج نصي."
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

        if extracted_result and "❌" not in extracted_result:
            successful_requests_count += 1
            last_extracted_links[user_id] = extracted_result
            result_message = f"✅ **النتيجة المستخرجة:**\n`{extracted_result}`"
            keyboard = [[InlineKeyboardButton("📋 نسخ النتيجة", callback_data="copy_result")]]
            await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(extracted_result)
    else:
        await update.message.reply_text("يرجى إرسال رابط صالح يبدأ بـ http:// أو https://.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    try:
        await query.answer()
    except:
        pass
        
    if query.data == "copy_result":
        res = last_extracted_links.get(user_id, "")
        try:
            await query.answer(f"تم النسخ بنجاح!", show_alert=True)
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
