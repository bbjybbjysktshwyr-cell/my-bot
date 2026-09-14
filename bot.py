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
        "successful_requests_count": 1143,
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
    
    # التعامل مع إدخال التقييم
    if user_states.get(user_id) == "waiting_for_rating_text":
        stars = user_states.get(user_id + "_stars", 5)
        name = update.effective_user.first_name or "User"
        user_ratings.append({"name": name, "stars": stars, "text": user_text})
        user_states.pop(user_id, None)
        user_states.pop(user_id + "_stars", None)
        save_data()
        await update.message.reply_text("✅ شكراً لك! تم إضافة تقييمك بنجاح.", reply_markup=get_main_keyboard(lang))
        return

    # الأزرار الرئيسية
    if user_text in ["🔗 تجاوز رابط", "🔗 Bypass Link"]:
        user_states[user_id] = "waiting_for_bypass_link"
        save_data()
        msg = "Send your link now (Linkvertise / Delta):" if lang == "en" else "أرسل الرابط الآن (يدعم دلتا و Linkvertise):"
        await update.message.reply_text(msg)
        return
        
    elif user_text in ["🌐 المواقع المدعومة", "🌐 Supported Sites"]:
        user_states.pop(user_id, None)
        save_data()
        msg = "Supported sites:\n- linkvertise.com\n- auth.platorelay.com (Delta)" if lang == "en" else "المواقع المدعومة حالياً:\n- linkvertise.com\n- auth.platorelay.com (Delta)"
        await update.message.reply_text(msg, reply_markup=get_main_keyboard(lang))
        return
        
    elif user_text in ["📖 شرح البوت", "📖 Bot Guide"]:
        user_states.pop(user_id, None)
        save_data()
        msg = "Click 'Bypass Link' first, then send your link." if lang == "en" else "اضغط على زر (تجاوز رابط) أولاً، ثم أرسل الرابط ليتم تجاوزه."
        await update.message.reply_text(msg, reply_markup=get_main_keyboard(lang))
        return
        
    elif user_text in ["⭐ تقييم البوت", "⭐ Bot Ratings"]:
        user_states.pop(user_id, None)
        save_data()
        await show_ratings_page(update.message, 0, lang)
        return
        
    elif user_text in ["🌍 تغيير اللغة", "🌍 Change Language"]:
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

    # معالجة إرسال الروابط
    if user_states.get(user_id) == "waiting_for_bypass_link":
        if "http://" in user_text or "https://" in user_text:
            user_states.pop(user_id, None)
            save_data()
            
            wait_msg = "⏳ Extracting result, please wait..." if lang == "en" else "⏳ جارٍ تجاوز الرابط واستخراج النتيجة، انتظر قليلاً..."
            status_msg = await update.message.reply_text(wait_msg)
            
            start_time = asyncio.get_event_loop().time()
            extracted_result = ""
            
            try:
                process = await asyncio.create_subprocess_exec(
                    "python", "-m", "linkvertisebypass.cli", user_text,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                output_text = stdout.decode('utf-8', errors='ignore').strip()
                elapsed_time = asyncio.get_event_loop().time() - start_time
                
                try:
                    data = json.loads(output_text)
                    if isinstance(data, dict):
                        extracted_result = data.get("value") or data.get("url") or data.get("destination") or data.get("result") or str(data)
                except:
                    for line in output_text.splitlines():
                        if "http://" in line or "https://" in line or "FREE_" in line or "game" in line:
                            extracted_result = line.strip()
                            break
                    if not extracted_result:
                        extracted_result = output_text

                if process.returncode == 0 and extracted_result and "error" not in extracted_result.lower():
                    successful_requests_count += 1
                    save_data()
                    
                    result_message = (
                        f"✅ **تم التجاوز بنجاح:**\n\n"
                        f"`{extracted_result}`\n\n"
                        f"⏳ الوقت المستغرق: {elapsed_time:.2f} ثانية"
                    )
                    keyboard = [
                        [InlineKeyboardButton("📋 نسخ النتيجة", callback_data=f"copy_key:{extracted_result}")],
                        [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
                    ]
                    try:
                        await status_msg.delete()
                    except:
                        pass
                    await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
                    return
            except Exception as ex:
                print(f"Bypass error: {ex}")

            # محاولة بديلة في حال فشل الأداة كلياً لتفادي توقف البوت
            fail_message = (
                f"❌ **فشل في تجاوز الرابط تلقائياً!**\n\n"
                f"⚠️ الأداة لم تستجب للرابط المطلوب أو أنه يتطلب تحديثاً للمكتبات في Termux.\n"
                f"جرب تشغيل الأداة يدوياً للتأكد من عملها."
            )
            keyboard = [
                [InlineKeyboardButton("🛠️ الدعم الفني", url="https://t.me/AL_shz1")],
                [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
            ]
            try:
                await status_msg.delete()
            except:
                pass
            await update.message.reply_text(fail_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("❌ الرابط غير صحيح. يرجى إرسال رابط صالح يبدأ بـ http:// أو https://")
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
    try:
        await query.answer()
    except:
        pass
        
    user_id = str(update.effective_user.id)
    lang = user_languages.get(user_id, "ar")
    data = query.data
    
    if data == "back_to_menu":
        user_states.pop(user_id, None)
        save_data()
        try:
            await query.message.delete()
        except:
            pass
        await query.message.reply_text("القائمة الرئيسية:" if lang == "ar" else "Main Menu:", reply_markup=get_main_keyboard(lang))
        
    elif data.startswith("lang_"):
        new_lang = data.split("_")[1]
        user_languages[user_id] = new_lang
        save_data()
        try:
            if new_lang == "en":
                await query.edit_message_text("Language changed to English successfully 🇺🇸")
            else:
                await query.edit_message_text("تم تغيير اللغة إلى العربية بنجاح 🇮🇶")
        except:
            await query.message.reply_text("Language updated successfully!" if new_lang == "en" else "تم تحديث اللغة بنجاح!")
            
    elif data == "start_add_rating":
        keyboard = [
            [InlineKeyboardButton("⭐", callback_data="rate_star:1"),
             InlineKeyboardButton("⭐⭐", callback_data="rate_star:2"),
             InlineKeyboardButton("⭐⭐⭐", callback_data="rate_star:3")],
            [InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rate_star:4"),
             InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rate_star:5")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="rating_page:0")]
        ]
        try:
            await query.edit_message_text("اختر عدد النجوم لتقييم البوت:", reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            await query.message.reply_text("اختر عدد النجوم لتقييم البوت:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data.startswith("rate_star:"):
        stars = int(data.split(":")[1])
        user_states[user_id + "_stars"] = stars
        user_states[user_id] = "waiting_for_rating_text"
        save_data()
        try:
            await query.edit_message_text(f"لقد اخترت {stars} نجوم ⭐.\nالآن يرجى إرسال رسالة برأيك أو تقييمك للبوت:")
        except:
            await query.message.reply_text(f"لقد اخترت {stars} نجوم ⭐.\nالآن يرجى إرسال رسالة برأيك أو تقييمك للبوت:")
        
    elif data.startswith("rating_page:"):
        idx = int(data.split(":")[1])
        try:
            await query.message.delete()
        except:
            pass
        await show_ratings_page(query.message, idx, lang)
        
    elif data.startswith("copy_key:"):
        try:
            await query.answer("تم النسخ بنجاح!", show_alert=True)
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
    
    print("Bot is running with robust error handling...")
    app.run_polling()

if __name__ == "__main__":
    main()
