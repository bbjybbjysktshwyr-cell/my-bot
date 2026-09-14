import os
import json
import asyncio
import subprocess
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "successful_requests_count": 1138,
        "user_ratings": [
            {"name": "Mohamed", "stars": 5, "text": "كويس جدا ويسهل عليك وقت كبير"},
            {"name": "معصومة بلال", "stars": 5, "text": "فوللل جربووو"},
            {"name": "Cristiano", "stars": 5, "text": "ياخي اسطوره الي اخترع هادا البوت"}
        ]
    }

def save_data():
    data = {
        "successful_requests_count": successful_requests_count,
        "user_ratings": user_ratings
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()
successful_requests_count = db["successful_requests_count"]
user_ratings = db["user_ratings"]

user_languages = {}
user_states = {}

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, "ar")
    user_states.pop(user_id, None)
    
    if lang == "en":
        welcome_text = "Welcome to the Link Bypass Bot 👋\n\nChoose a service from the menu:"
    else:
        welcome_text = "مرحباً بك في بوت تجاوز الروابط 👋\n\nاختر الخدمة من القائمة:"
        
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(lang))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global successful_requests_count
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, "ar")
    user_text = update.message.text
    
    if user_states.get(user_id) == "waiting_for_rating_text":
        stars = user_states.get(user_id + 1000, 5)
        name = update.effective_user.first_name or "User"
        user_ratings.append({"name": name, "stars": stars, "text": user_text})
        save_data()
        user_states.pop(user_id, None)
        user_states.pop(user_id + 1000, None)
        
        await update.message.reply_text("✅ شكراً لك! تم إضافة تقييمك بنجاح.", reply_markup=get_main_keyboard(lang))
        return

    if user_text in ["🔗 تجاوز رابط", "🔗 Bypass Link"]:
        user_states[user_id] = "waiting_for_bypass_link"
        msg = "Send your link now (Delta or Linkvertise):" if lang == "en" else "أرسل الرابط الآن (يدعم دلتا و Linkvertise):"
        await update.message.reply_text(msg)
        return
        
    elif user_text in ["🌐 المواقع المدعومة", "🌐 Supported Sites"]:
        user_states.pop(user_id, None)
        msg = (
            "🌐 المواقع المدعومة:\n\n"
            "1️⃣ auth.platorelay.com (Delta) - مدعوم ✅\n"
            "2️⃣ linkvertise.com / link-to.net - مدعوم (عبر shadows.py) ✅"
        ) if lang != "en" else (
            "🌐 Supported Sites:\n\n"
            "1️⃣ auth.platorelay.com (Delta) - Supported ✅\n"
            "2️⃣ linkvertise.com / link-to.net - Supported (via shadows.py) ✅"
        )
        await update.message.reply_text(msg)
        return
        
    elif user_text in ["📖 شرح البوت", "📖 Bot Guide"]:
        user_states.pop(user_id, None)
        msg = "Click 'Bypass Link' first, then send your link." if lang == "en" else "اضغط على زر (تجاوز رابط) أولاً، ثم أرسل الرابط ليتم استخراج النتيجة."
        await update.message.reply_text(msg)
        return
        
    elif user_text in ["⭐ تقييم البوت", "⭐ Bot Ratings"]:
        user_states.pop(user_id, None)
        await show_ratings_page(update.message, 0, lang)
        return
        
    elif user_text in ["🌍 تغيير اللغة", "🌍 Change Language"]:
        user_states.pop(user_id, None)
        lang_text = "Please choose your language 👇" if lang == "en" else "👇 الرجاء اختيار اللغة 👇"
        keyboard = [
            [InlineKeyboardButton("🇮🇶 العربية", callback_data="lang_ar"),
             InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
        ]
        await update.message.reply_text(lang_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
        
    elif "الطلبات الناجحة" in user_text or "Successful Requests" in user_text:
        user_states.pop(user_id, None)
        msg = f"📊 Total successful requests: {successful_requests_count}" if lang == "en" else f"📊 عدد الطلبات الناجحة عبر البوت حتى الآن: {successful_requests_count}"
        await update.message.reply_text(msg)
        return

    if user_states.get(user_id) == "waiting_for_bypass_link":
        user_states.pop(user_id, None)
        wait_msg = "⏳ Extracting, please wait..." if lang == "en" else "⏳ جارٍ حل الرابط، انتظر قليلاً..."
        status_msg = await update.message.reply_text(wait_msg)
        
        start_time = asyncio.get_event_loop().time()
        try:
            script_to_run = "main.py"
            if "linkvertise" in user_text.lower() or "link-to.net" in user_text.lower():
                script_to_run = "shadows.py"

            process = await asyncio.create_subprocess_exec(
                "python", script_to_run, user_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            output_text = stdout.decode('utf-8')
            elapsed_time = asyncio.get_event_loop().time() - start_time
            
            extracted_result = ""
            for line in output_text.splitlines():
                line_str = line.strip()
                if "FREE_" in line_str or "http://" in line_str or "https://" in line_str:
                    if user_text not in line_str:
                        extracted_result = line_str
                        break
            
            if not extracted_result:
                for line in output_text.splitlines():
                    if "KEY" in line and "NOT_FOUND" not in line:
                        extracted_result = line.strip()
                        break

            if process.returncode == 0 and extracted_result:
                successful_requests_count += 1
                save_data()
                
                result_message = (
                    f"🔗 **النتيجة المستخرجة:**\n`{extracted_result}`\n\n"
                    f"⏳ الوقت المستغرق: {elapsed_time:.2f} ثانية"
                )

                keyboard = [
                    [InlineKeyboardButton("📋 نسخ النتيجة", callback_data=f"copy_key:{extracted_result}")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
                ]
                
                await status_msg.delete()
                await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                fail_message = (
                    f"❌ **فشل في تجاوز الرابط!**\n\n"
                    f"⚠️ نعتذر منك، يبدو أن الرابط غير صالح أو تتطلب الأداة متطلبات إضافية.\n"
                    f"يرجى التأكد من تشغيل الأداة يدوياً أولاً للتأكد من تثبيت مكتباتها."
                )
                keyboard = [
                    [InlineKeyboardButton("🛠️ الدعم الفني", url="https://t.me/AL_shz1")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
                ]
                await status_msg.delete()
                await update.message.reply_text(fail_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
                
        except Exception as e:
            await status_msg.edit_text(f"Error: {str(e)}")
    else:
        await update.message.reply_text("⚠️ يرجى الضغط على زر **(🔗 تجاوز رابط)** من القائمة أدناه أولاً قبل إرسال الرابط.")

async def show_ratings_page(message_obj, index, lang="ar"):
    if not user_ratings:
        await message_obj.reply_text("No ratings yet." if lang == "en" else "لا توجد تقييمات حالياً.")
        return
        
    total = len(user_ratings)
    index = max(0, min(index, total - 1))
    r = user_ratings[index]
    
    stars_str = "⭐" * r["stars"]
    ratings_content = (
        f"⭐ **التقييمات ({index + 1}/{total}):**\n\n"
        f"👤 **{r['name']}** {stars_str}\n"
        f"{r['text']}"
    )
    
    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"rating_page:{index - 1}"))
    if index < total - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"rating_page:{index + 1}"))
        
    keyboard = []
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("➕ إضافة تقييم", callback_data="start_add_rating")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")])
    
    await message_obj.reply_text(ratings_content, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, "ar")
    
    data = query.data
    
    if data == "back_to_menu":
        user_states.pop(user_id, None)
        await query.message.delete()
        await query.message.reply_text("القائمة الرئيسية:" if lang == "ar" else "Main Menu:", reply_markup=get_main_keyboard(lang))
        
    elif data.startswith("lang_"):
        new_lang = data.split("_")[1]
        user_languages[user_id] = new_lang
        if new_lang == "en":
            await query.edit_message_text("Language changed to English successfully 🇺🇸")
        else:
            await query.edit_message_text("تم تغيير اللغة إلى العربية بنجاح 🇮🇶")
            
    elif data ==غ elif data == "start_add_rating":
        keyboard = [
            [InlineKeyboardButton("⭐", callback_data="rate_star:1"),
             InlineKeyboardButton("⭐⭐", callback_data="rate_star:2"),
             InlineKeyboardButton("⭐⭐⭐", callback_data="rate_star:3")],
            [InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rate_star:4"),
             InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rate_star:5")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="rating_page:0")]
        ]
        await query.edit_message_text("اختر عدد النجوم لتقييم البوت:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data.startswith("rate_star:"):
        stars = int(data.split(":")[1])
        user_states[user_id + 1000] = stars
        user_states[user_id] = "waiting_for_rating_text"
        await query.edit_message_text(f"لقد اخترت {stars} نجوم ⭐.\nالآن يرجى إرسال رسالة برأيك أو تقييمك للبوت:")
        
    elif data.startswith("rating_page:"):
        idx = int(data.split(":")[1])
        await query.message.delete()
        await show_ratings_page(query.message, idx, lang)
        
    elif data.startswith("copy_key:"):
        key_to_copy = data.split(":", 1)[1]
        await query.answer(f"تم نسخ النتيجة: {key_to_copy}", show_alert=True)

def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running with shadows.py integrated...")
    app.run_polling()

if __name__ == "__main__":
    main()
