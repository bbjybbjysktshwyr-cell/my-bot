import os
import sys
import asyncio
import subprocess
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

successful_requests_count = 1136
user_languages = {}
user_ratings = [
    {"name": "Mohamed", "stars": 5, "text": "كويس جدا ويسهل عليك وقت كبير"},
    {"name": "معصومة بلال", "stars": 5, "text": "فوللل جربووو"},
    {"name": "Cristiano", "stars": 5, "text": "ياخي اسطوره الي اخترع هادا البوت"}
]
user_states = {}
last_extracted_links = {}

def get_main_keyboard(lang="ar"):
    keyboard = [
        ["🔗 تجاوز رابط"],
        ["🌐 المواقع المدعومة", "📖 شرح البوت"],
        ["⭐ تقييم البوت", "🌍 تغيير اللغة"],
        [f"📊 الطلبات الناجحة: {successful_requests_count}"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك في بوت تجاوز الروابط 👋\n\nأرسل رابط دلتا أو أي رابط مباشرة:", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global successful_requests_count
    if not update.message or not update.message.text:
        return
        
    user_id = update.effective_user.id
    user_text = update.message.text.strip()
    
    if user_text in ["🔗 تجاوز رابط"]:
        await update.message.reply_text("أرسل رابطك الآن وسأقوم باستخراجه فوراً:")
        return
    elif user_text in ["🌐 المواقع المدعومة"]:
        await update.message.reply_text("المواقع المدعومة:\n- auth.platorelay.com (Delta)\n- linkvertise.com")
        return
    elif user_text in ["📖 شرح البوت"]:
        await update.message.reply_text("فقط أرسل الرابط مباشرة وسيتم تجاوزه.")
        return
    elif user_text in ["⭐ تقييم البوت"]:
        await update.message.reply_text("⭐ التقييمات ممتازة!")
        return
    elif user_text in ["🌍 تغيير اللغة"]:
        await update.message.reply_text("اللغة الحالية هي العربية.")
        return
    elif "الطلبات الناجحة" in user_text:
        await update.message.reply_text(f"📊 عدد الطلبات الناجحة: {successful_requests_count}")
        return

    if "http://" in user_text or "https://" in user_text:
        status_msg = await update.message.reply_text("⏳ جارٍ معالجة الرابط عبر أداتك الأصلية...")
        
        extracted_result = ""
        try:
            # استدعاء main.py ومعالجة الرابط مع مهلة زمنية لكي لا يعلق البوت أبداً
            process = await asyncio.create_subprocess_exec(
                "python3", "main.py", user_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=20)
                output_text = stdout.decode('utf-8', errors='ignore')
                
                # البحث عن النتيجة داخل المخرجات
                for line in output_text.splitlines():
                    line_str = line.strip()
                    if "http://" in line_str or "https://" in line_str or "FREE_" in line_str or "Key" in line_str:
                        if user_text not in line_str and "platorelay" not in line_str:
                            extracted_result = line_str
                            break
                if not extracted_result and output_text:
                    lines = [l.strip() for l in output_text.splitlines() if l.strip() and not l.startswith("Traceback")]
                    if lines:
                        extracted_result = lines[-1]
            except asyncio.TimeoutError:
                process.kill()
                extracted_result = ""
        except Exception as e:
            print(f"Error: {e}")
            
        try:
            await status_msg.delete()
        except:
            pass

        if extracted_result:
            successful_requests_count += 1
            last_extracted_links[user_id] = extracted_result
            result_message = f"✅ **النتيجة المستخرجة:**\n`{extracted_result}`"
            keyboard = [[InlineKeyboardButton("📋 نسخ النتيجة", callback_data="copy_result")]]
            await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("❌ لم يتم العثور على مفتاح أو استجابة من أداة main.py. تأكد أن ملف main.py يطبع النتيجة مباشرة.")
    else:
        await update.message.reply_text("يرجى إرسال رابط صحيح.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    if query.data == "copy_result":
        res = last_extracted_links.get(user_id, "")
        try:
            await query.answer(f"النتيجة: {res}", show_alert=True)
        except:
            pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running with main.py integration...")
    app.run_polling()

if __name__ == "__main__":
    main()
