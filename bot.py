import os
import asyncio
import subprocess
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

# المتغيرات العامة للبوت
successful_requests_count = 1136
user_languages = {}  # حفظ لغة المستخدم (ar / en)
user_ratings = [
    {"name": "Mohamed", "stars": 5, "text": "كويس جدا ويسهل عليك وقت كبير"},
    {"name": "معصومة بلال", "stars": 5, "text": "فوللل جربووو"},
    {"name": "Cristiano", "stars": 5, "text": "ياخي اسطوره الي اخترع هادا البوت"}
]
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
    
    # التحقق مما إذا كان المستخدم في حالة إرسال نص تقييم
    if user_states.get(user_id) == "waiting_for_rating_text":
        stars = user_states.get(user_id + 1000, 5)
        name = update.effective_user.first_name or "User"
        user_ratings.append({"name": name, "stars": stars, "text": user_text})
        user_states.pop(user_id, None)
        user_states.pop(user_id + 1000, None)
        
        await update.message.reply_text("✅ شكراً لك! تم إضافة تقييمك بنجاح.", reply_markup=get_main_keyboard(lang))
        return

    # الأزرار والخدمات
    if user_text in ["🔗 تجاوز رابط", "🔗 Bypass Link"]:
        msg = "Send your Delta link now (e.g., https://auth.platorelay.com/...):" if lang == "en" else "أرسل رابط دلتا الآن (مثل: https://auth.platorelay.com/...) لأقوم باستخراج المفتاح لك."
        await update.message.reply_text(msg)
        return
        
    elif user_text in ["🌐 المواقع المدعومة", "🌐 Supported Sites"]:
        msg = "Supported sites:\n- auth.platorelay.com (Delta)" if lang == "en" else "الموقع المدعوم حالياً:\n- auth.platorelay.com (Delta)"
        await update.message.reply_text(msg)
        return
        
    elif user_text in ["📖 شرح البوت", "📖 Bot Guide"]:
        msg = "Just send your link and the bot will handle it in the background." if lang == "en" else "فقط قم بإرسال رابط التجاوز الخاص بك وسيقوم البوت باستخراج المفتاح تلقائياً."
        await update.message.reply_text(msg)
        return
        
    elif user_text in ["⭐ تقييم البوت", "⭐ Bot Ratings"]:
        await show_ratings_page(update.message, 0, lang)
        return
        
    elif user_text in ["🌍 تغيير اللغة", "🌍 Change Language"]:
        lang_text = "Please choose your language 👇" if lang == "en" else "👇 الرجاء اختيار اللغة 👇"
        keyboard = [
            [InlineKeyboardButton("🇮🇶 العربية", callback_data="lang_ar"),
             InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
        ]
        await update.message.reply_text(lang_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
        
    elif "الطلبات الناجحة" in user_text or "Successful Requests" in user_text:
        msg = f"📊 Total successful requests: {successful_requests_count}" if lang == "en" else f"📊 عدد الطلبات الناجحة عبر البوت حتى الآن: {successful_requests_count}"
        await update.message.reply_text(msg)
        return

    # معالجة روابط دلتا والاستخراج
    if "platorelay.com" in user_text or "d=" in user_text:
        wait_msg = "⏳ Extracting key, please wait..." if lang == "en" else "⏳ جارٍ حل الرابط واستخراج المفتاح، انتظر قليلاً..."
        status_msg = await update.message.reply_text(wait_msg)
        
        start_time = asyncio.get_event_loop().time()
        try:
            process = await asyncio.create_subprocess_exec(
                "python", "main.py", user_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            output_text = stdout.decode('utf-8')
            elapsed_time = asyncio.get_event_loop().time() - start_time
            
            # البحث عن المفتاح
            extracted_key = ""
            for line in output_text.splitlines():
                if "FREE_" in line:
                    extracted_key = line.strip()
                    break
            if not extracted_key:
                for line in output_text.splitlines():
                    if "KEY" in line and "NOT_FOUND" not in line:
                        extracted_key = line.strip()
                        break

            if process.returncode == 0 and extracted_key:
                successful_requests_count += 1
                
                result_message = (
                    f"🔑 `{extracted_key}`\n\n"
                    f"⏳ الوقت المستغرق: {elapsed_time:.2f} ثانية\n\n"
                    f"🔔:\n"
                    f"اضغط على المفتاح أعلاه للنسخ السريع، أو استخدم زر نسخ المفتاح بالأسفل."
                )

                keyboard = [
                    [InlineKeyboardButton("📋 نسخ المفتاح", callback_data=f"copy_key:{extracted_key}")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
                ]
                
                await status_msg.delete()
                await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                # رسالة الفشل مع زر الدعم الفني وحسابك الشخصي
                fail_message = (
                    f"❌ **فشل في استخراج المفتاح!**\n\n"
                    f"⚠️ نعتذر منك، يبدو أن الرابط منتهي الصلاحية أو غير صالح.\n"
                    f"يرجى توليد رابط جديد وإرساله مرة أخرى."
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
        err_msg = "Please choose an option from the menu or send a valid link." if lang == "en" else "يرجى اختيار أمر من القائمة أو إرسال رابط صحيح."
        await update.message.reply_text(err_msg)

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
        await query.message.delete()
        await query.message.reply_text("القائمة الرئيسية:" if lang == "ar" else "Main Menu:", reply_markup=get_main_keyboard(lang))
        
    elif data.startswith("lang_"):
        new_lang = data.split("_")[1]
        user_languages[user_id] = new_lang
        if new_lang == "en":
            await query.edit_message_text("Language changed to English successfully 🇺🇸")
        else:
            await query.edit_message_text("تم تغيير اللغة إلى العربية بنجاح 🇮🇶")
            
    elif data == "start_add_rating":
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
        await query.answer(f"تم نسخ المفتاح: {key_to_copy}", show_alert=True)

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
    
    print("Bot is running with full fixes and support button...")
    app.run_polling()

if __name__ == "__main__":
    main()
