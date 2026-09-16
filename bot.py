import os
import urllib.parse
import urllib.request
import json
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
    if lang == "en":
        keyboard = [
            ["🔗 Bypass Link"],
            ["🌐 Supported Sites", "📖 Bot Guide"],
            ["⭐ Bot Ratings", "🌍 Change Language"],
            [f"📊 Successful Requests: {successful_requests_count}"]
        ]
    else:
        keyboard = [
            ["🔗 تجاوز رابط"],
            ["🌐 المواقع المدعومة", "📖 شرح البوت"],
            ["⭐ تقييم البوت", "🌍 تغيير اللغة"],
            [f"📊 الطلبات الناجحة: {successful_requests_count}"]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def bypass_link_api(url: str) -> str:
    """تجاوز سريع جداً عبر الـ API بدون تعليق Termux"""
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        # استخدام API عام ومستقر لتجاوز روابط دلتا ولينكفايتز
        api_url = f"https://bypass.bot.nu/bypass2?url={encoded_url}"
        
        req = urllib.request.Request(
            api_url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            for key in ["destination", "result", "url", "key"]:
                if key in data and data[key]:
                    val = str(data[key])
                    if val.startswith("http") or len(val) > 10:
                        return val
    except Exception as e:
        print(f"API Error: {e}")
    return ""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, "ar")
    welcome_text = "Welcome to the Bypass Bot 👋\n\nSend your link directly:" if lang == "en" else "مرحباً بك في بوت تجاوز الروابط 👋\n\nأرسل الرابط مباشرة وسأقوم باستخراجه فوراً:"
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(lang))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global successful_requests_count
    if not update.message or not update.message.text:
        return
        
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, "ar")
    user_text = update.message.text.strip()
    
    if user_states.get(user_id) == "waiting_for_rating_text":
        stars = user_states.get(user_id + 1000, 5)
        name = update.effective_user.first_name or "User"
        user_ratings.append({"name": name, "stars": stars, "text": user_text})
        user_states.pop(user_id, None)
        user_states.pop(user_id + 1000, None)
        await update.message.reply_text("✅ شكراً لك! تم إضافة تقييمك بنجاح.", reply_markup=get_main_keyboard(lang))
        return

    if user_text in ["🔗 تجاوز رابط", "🔗 Bypass Link"]:
        await update.message.reply_text("أرسل رابطك الآن وسأقوم باستخراجه فوراً:")
        return
    elif user_text in ["🌐 المواقع المدعومة", "🌐 Supported Sites"]:
        await update.message.reply_text("المواقع المدعومة:\n- auth.platorelay.com (Delta)\n- linkvertise.com")
        return
    elif user_text in ["📖 شرح البوت", "📖 Bot Guide"]:
        await update.message.reply_text("فقط أرسل الرابط مباشرة وسيتم تجاوزه خلال ثوانٍ.")
        return
    elif user_text in ["⭐ تقييم البوت", "⭐ Bot Ratings"]:
        await show_ratings_page_message(update.message, 0, lang)
        return
    elif user_text in ["🌍 تغيير اللغة", "🌍 Change Language"]:
        keyboard = [[InlineKeyboardButton("🇮🇶 العربية", callback_data="lang_ar"), InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]]
        await update.message.reply_text("اختر اللغة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif "الطلبات الناجحة" in user_text or "Successful Requests" in user_text:
        await update.message.reply_text(f"📊 عدد الطلبات الناجحة: {successful_requests_count}")
        return

    if "http://" in user_text or "https://" in user_text:
        status_msg = await update.message.reply_text("⏳ جارٍ استخراج النتيجة...")
        
        # تنفيذ الاستخراج بشكل فوري بدون تعليق
        extracted_result = bypass_link_api(user_text)
        
        try:
            await status_msg.delete()
        except:
            pass

        if extracted_result:
            successful_requests_count += 1
            last_extracted_links[user_id] = extracted_result
            
            result_message = f"✅ **النتيجة المستخرجة:**\n`{extracted_result}`"
            keyboard = [
                [InlineKeyboardButton("📋 نسخ النتيجة", callback_data="copy_result")],
                [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
            ]
            await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("❌ عذراً، لم يتم استخراج الرابط أو أن الموقع استجاب ببطء. جرب مرة أخرى.")
    else:
        await update.message.reply_text("يرجى إرسال رابط صحيح يبدأ بـ http://")

async def show_ratings_page_message(message_obj, index, lang="ar"):
    if not user_ratings:
        await message_obj.reply_text("No ratings yet.")
        return
    total = len(user_ratings)
    index = max(0, min(index, total - 1))
    r = user_ratings[index]
    stars_str = "⭐" * r["stars"]
    ratings_content = f"⭐ **التقييمات ({index + 1}/{total}):**\n\n👤 **{r['name']}** {stars_str}\n{r['text']}"
    
    keyboard = [[InlineKeyboardButton("➕ إضافة تقييم", callback_data="start_add_rating")], [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]]
    await message_obj.reply_text(ratings_content, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id
    
    if data == "back_to_menu":
        try:
            await query.message.delete()
        except:
            pass
        await context.bot.send_message(chat_id=update.effective_chat.id, text="القائمة الرئيسية:", reply_markup=get_main_keyboard())
    elif data == "copy_result":
        res = last_extracted_links.get(user_id, "")
        try:
            await query.answer(f"النتيجة: {res}", show_alert=True)
        except:
            pass
    elif data == "start_add_rating":
        user_states[user_id] = "waiting_for_rating_text"
        try:
            await query.edit_message_text("أرسل تقييمك برسالة نصية الآن:")
        except:
            pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running smoothly...")
    app.run_polling()

if __name__ == "__main__":
    main()
