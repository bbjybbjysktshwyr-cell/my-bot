import os
import json
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

try:
    from linkvertisebypass import bypass as bypass_link_func
except ImportError:
    bypass_link_func = None

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
        "successful_requests_count": 1147,
        "user_ratings": [
            {"name": "Mohamed", "stars": 5, "text": "كويس جدا ويسهل عليك وقت كبير"},
            {"name": "معصومة بلال", "stars": 5, "text": "فوللل جربووو"},
            {"name": "Cristiano", "stars": 5, "text": "ياخي اسطوره الي اخترع هادا البوت"}
        ],
        "user_languages": {},
        "user_states": {}
    }

def save_data():
    data = {
        "successful_requests_count": successful_requests_count,
        "user_ratings": user_ratings,
        "user_languages": user_languages,
        "user_states": user_states
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()
successful_requests_count = db["successful_requests_count"]
user_ratings = db["user_ratings"]
user_languages = db.get("user_languages", {})
user_states = db.get("user_states", {})

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
    user_id = str(update.effective_user.id)
    lang = user_languages.get(user_id, "ar")
    user_states.pop(user_id, None)
    save_data()
    
    welcome_text = "Welcome to the Link Bypass Bot 👋\n\nChoose a service from the menu:" if lang == "en" else "مرحباً بك في بوت تجاوز الروابط 👋\n\nاختر الخدمة من القائمة:"
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(lang))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global successful_requests_count
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    lang = user_languages.get(user_id, "ar")
    user_text = update.message.text.strip()
    
    if user_states.get(user_id) == "waiting_for_rating_text":
        stars = user_states.get(user_id + "_stars", 5)
        name = update.effective_user.first_name or "User"
        user_ratings.append({"name": name, "stars": stars, "text": user_text})
        user_states.pop(user_id, None)
        user_states.pop(user_id + "_stars", None)
        save_data()
        await update.message.reply_text("✅ شكراً لك! تم إضافة تقييمك بنجاح.", reply_markup=get_main_keyboard(lang))
        return

    if "تجاوز رابط" in user_text or "Bypass Link" in user_text:
        user_states[user_id] = "waiting_for_bypass_link"
        save_data()
        msg = "Send your link now:" if lang == "en" else "أرسل الرابط الآن:"
        await update.message.reply_text(msg)
        return
        
    elif "المواقع المدعومة" in user_text or "Supported Sites" in user_text:
        user_states.pop(user_id, None)
        save_data()
        msg = "Supported sites:\n- linkvertise.com" if lang == "en" else "المواقع المدعومة حالياً:\n- linkvertise.com"
        await update.message.reply_text(msg, reply_markup=get_main_keyboard(lang))
        return
        
    elif "شرح البوت" in user_text or "Bot Guide" in user_text:
        user_states.pop(user_id, None)
        save_data()
        msg = "Click 'Bypass Link' first, then send your link." if lang == "en" else "اضغط على زر (تجاوز رابط) أولاً، ثم أرسل الرابط ليتم تجاوزه."
        await update.message.reply_text(msg, reply_markup=get_main_keyboard(lang))
        return
        
    elif "تقييم البوت" in user_text or "Bot Ratings" in user_text:
        user_states.pop(user_id, None)
        save_data()
        await show_ratings_page(update, context, 0, lang, edit=False)
        return
        
    elif "تغيير اللغة" in user_text or "Change Language" in user_text:
        user_states.pop(user_id, None)
        save_data()
        lang_text = "Please choose your language 👇" if lang == "en" else "👇 الرجاء اختيار اللغة 👇"
        keyboard = [
            [InlineKeyboardButton("🇮🇶 العربية", callback_data="lang_ar"),
             InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
        ]
        await update.message.reply_text(lang_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
        
    elif "الطلبات الناجحة" in user_text or "Successful Requests" in user_text:
        user_states.pop(user_id, None)
        save_data()
        msg = f"📊 Total successful requests: {successful_requests_count}" if lang == "en" else f"📊 عدد الطلبات الناجحة عبر البوت حتى الآن: {successful_requests_count}"
        await update.message.reply_text(msg, reply_markup=get_main_keyboard(lang))
        return

    if user_states.get(user_id) == "waiting_for_bypass_link":
        if "http://" in user_text or "https://" in user_text:
            user_states.pop(user_id, None)
            save_data()
            
            wait_msg = "⏳ Extracting result, please wait..." if lang == "en" else "⏳ جارٍ تجاوز الرابط واستخراج النتيجة، انتظر قليلاً..."
            status_msg = await update.message.reply_text(wait_msg)
            
            start_time = asyncio.get_event_loop().time()
            extracted_result = ""
            
            try:
                loop = asyncio.get_running_loop()
                if bypass_link_func:
                    res = await loop.run_in_executor(None, bypass_link_func, user_text)
                    if hasattr(res, "value") and res.value:
                        extracted_result = str(res.value)
                    elif hasattr(res, "url") and res.url:
                        extracted_result = str(res.url)
                    elif hasattr(res, "result") and res.result:
                        extracted_result = str(res.result)
                    else:
                        extracted_result = str(res)
                else:
                    process = await asyncio.create_subprocess_exec(
                        "python3", "-m", "linkvertisebypass", user_text,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()
                    extracted_result = stdout.decode('utf-8', errors='ignore').strip()
            except Exception as ex:
                extracted_result = str(ex)

            elapsed_time = asyncio.get_event_loop().time() - start_time
            
            try:
                await status_msg.delete()
            except:
                pass

            res_lower = extracted_result.lower()
            if extracted_result and "unsupported" not in res_lower and "error" not in res_lower and "traceback" not in res_lower:
                successful_requests_count += 1
                save_data()
                
                result_message = (
                    f"✅ **تم التجاوز بنجاح:**\n\n"
                    f"`{extracted_result}`\n\n"
                    f"⏳ الوقت المستغرق: {elapsed_time:.2f} ثانية"
                )
                keyboard = [
                    [InlineKeyboardButton("📋 كيف أنسخ النتيجة؟", callback_data="copy_key")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
                ]
                await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                fail_message = (
                    f"❌ **فشل في تجاوز الرابط!**\n\n"
                    f"⚠️ الرابط غير مدعوم حالياً أو أن الأداة تتطلب تحديثاً."
                )
                keyboard = [
                    [InlineKeyboardButton("🛠️ الدعم الفني", url="https://t.me/AL_shz1")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
                ]
                await update.message.reply_text(fail_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("❌ الرابط غير صحيح. يرجى إرسال رابط صالح يبدأ بـ http:// أو https://")
    else:
        await update.message.reply_text("⚠️ يرجى الضغط على زر **(🔗 تجاوز رابط)** من القائمة أدناه أولاً قبل إرسال الرابط.")

async def show_ratings_page(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int, lang: str, edit: bool = False):
    if not user_ratings:
        msg = "No ratings yet." if lang == "en" else "لا توجد تقييمات حالياً."
        if edit:
            await update.callback_query.edit_message_text(msg)
        else:
            await update.message.reply_text(msg)
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
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    if edit:
        await update.callback_query.edit_message_text(ratings_content, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(ratings_content, parse_mode="Markdown", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except:
        pass
        
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    lang = user_languages.get(user_id, "ar")
    data = query.data
    
    if data == "back_to_menu":
        user_states.pop(user_id, None)
        save_data()
        try:
            await query.message.delete()
        except:
            pass
        await context.bot.send_message(
            chat_id=chat_id, 
            text="القائمة الرئيسية:" if lang == "ar" else "Main Menu:", 
            reply_markup=get_main_keyboard(lang)
        )
        
    elif data.startswith("lang_"):
        new_lang = data.split("_")[1]
        user_languages[user_id] = new_lang
        save_data()
        try:
            msg = "Language changed to English successfully 🇺🇸" if new_lang == "en" else "تم تغيير اللغة إلى العربية بنجاح 🇮🇶"
            await query.edit_message_text(msg)
            await context.bot.send_message(chat_id=chat_id, text="Main Menu:" if new_lang == "en" else "القائمة الرئيسية:", reply_markup=get_main_keyboard(new_lang))
        except:
            pass
            
    elif data == "start_add_rating":
        keyboard = [
            [InlineKeyboardButton("⭐", callback_data="rate_star:1"),
             InlineKeyboardButton("⭐⭐", callback_data="rate_star:2"),
             InlineKeyboardButton("⭐⭐⭐", callback_data="rate_star:3")],
            [InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rate_star:4"),
             InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rate_star:5")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="rating_page:0")]
        ]
        await query.edit_message_text("اختر عدد النجوم لتقييم البوت:" if lang == "ar" else "Choose stars:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data.startswith("rate_star:"):
        stars = int(data.split(":")[1])
        user_states[user_id + "_stars"] = stars
        user_states[user_id] = "waiting_for_rating_text"
        save_data()
        await query.edit_message_text(
            f"لقد اخترت {stars} نجوم ⭐.\nالآن يرجى إرسال رسالة برأيك أو تقييمك للبوت:" if lang == "ar" else f"You chose {stars} stars ⭐.\nNow send your review:"
        )
        
    elif data.startswith("rating_page:"):
        idx = int(data.split(":")[1])
        await show_ratings_page(update, context, idx, lang, edit=True)
        
    elif data == "copy_key":
        try:
            await query.answer("اضغط ضغطة مطولة على النتيجة في الرسالة لنسخها بسهولة!", show_alert=True)
        except:
            pass

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
    
    print("Bot is running perfectly...")
    app.run_polling()

if __name__ == "__main__":
    main()
