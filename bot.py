import os
import sys
import json
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
    welcome_text = "Welcome to the Link Bypass Bot 👋\n\nSend any link directly:" if lang == "en" else "مرحباً بك في بوت تجاوز الروابط 👋\n\nأرسل أي رابط مباشرة وسأقوم بحله:"
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
        msg = "Send your link now:" if lang == "en" else "أرسل رابطك الآن وسأقوم باستخراجه فوراً:"
        await update.message.reply_text(msg)
        return
        
    elif user_text in ["🌐 المواقع المدعومة", "🌐 Supported Sites"]:
        msg = "Supported sites:\n- auth.platorelay.com (Delta)\n- linkvertise.com" if lang == "en" else "المواقع المدعومة:\n- auth.platorelay.com (Delta)\n- linkvertise.com"
        await update.message.reply_text(msg)
        return
        
    elif user_text in ["📖 شرح البوت", "📖 Bot Guide"]:
        msg = "Just send your link directly!" if lang == "en" else "فقط أرسل الرابط مباشرة في المحادثة وسيتم تجاوزه."
        await update.message.reply_text(msg)
        return
        
    elif user_text in ["⭐ تقييم البوت", "⭐ Bot Ratings"]:
        await show_ratings_page_message(update.message, 0, lang)
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

    if "http://" in user_text or "https://" in user_text:
        wait_msg = "⏳ جارٍ حل الرابط واستخراج النتيجة..."
        status_msg = await update.message.reply_text(wait_msg)
        
        start_time = asyncio.get_event_loop().time()
        extracted_result = ""
        
        is_linkvertise = "linkvertise" in user_text.lower() or "link-to.net" in user_text.lower()
        
        if is_linkvertise:
            try:
                process = await asyncio.create_subprocess_exec(
                    "python", "-m", "linkvertisebypass.cli", user_text,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                output_text = stdout.decode('utf-8', errors='ignore').strip()
                error_text = stderr.decode('utf-8', errors='ignore').strip()
                
                if error_text and not output_text:
                    extracted_result = f"ERROR: {error_text[:300]}"
                else:
                    try:
                        data = json.loads(output_text)
                        if isinstance(data, dict):
                            extracted_result = data.get("url") or data.get("destination") or data.get("result") or ""
                    except json.JSONDecodeError:
                        pass
                        
                    if not extracted_result:
                        for line in output_text.splitlines():
                            if "http://" in line or "https://" in line:
                                if user_text not in line:
                                    extracted_result = line.strip()
                                    break
                        if not extracted_result and output_text:
                            extracted_result = output_text[:300]
            except Exception as e:
                extracted_result = f"EXC: {str(e)}"
        else:
            cmd = ["python", "main.py", user_text]
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                output_text = stdout.decode('utf-8', errors='ignore')
                
                for line in output_text.splitlines():
                    if "FREE_" in line or "http://" in line or "https://" in line or "Key" in line:
                        if user_text not in line:
                            extracted_result = line.strip()
                            break
                if not extracted_result:
                    lines = [l.strip() for l in output_text.splitlines() if l.strip() and not l.startswith("Traceback") and "127.0.0.1" not in l]
                    if lines:
                        extracted_result = lines[-1]
            except Exception as e:
                extracted_result = f"EXC: {str(e)}"
            
        elapsed_time = asyncio.get_event_loop().time() - start_time
        
        try:
            await status_msg.delete()
        except:
            pass

        if extracted_result:
            if not extracted_result.startswith("ERROR:") and not extracted_result.startswith("EXC:"):
                successful_requests_count += 1
            result_message = (
                f"✅ **النتيجة المستخرجة:**\n`{extracted_result}`\n\n"
                f"⏳ الوقت المستغرق: {elapsed_time:.2f} ثانية"
            )
            keyboard = [
                [InlineKeyboardButton("📋 نسخ النتيجة", callback_data=f"copy_key:{extracted_result}")],
                [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
            ]
            await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            fail_message = "❌ عذراً، فشل استخراج الرابط. تأكد من عمل الأداة الخاصة به."
            keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]]
            await update.message.reply_text(fail_message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("يرجى إرسال رابط صحيح يبدأ بـ http:// أو اختيار أمر من القائمة.")

async def show_ratings_page_message(message_obj, index, lang="ar"):
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
    except Exception:
        pass
    
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, "ar")
    data = query.data
    
    if data == "back_to_menu":
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="القائمة الرئيسية:" if lang == "ar" else "Main Menu:",
            reply_markup=get_main_keyboard(lang)
        )
        
    elif data.startswith("lang_"):
        new_lang = data.split("_")[1]
        user_languages[user_id] = new_lang
        msg = "Language changed to English successfully 🇺🇸" if new_lang == "en" else "تم تغيير اللغة إلى العربية بنجاح 🇮🇶"
        try:
            await query.edit_message_text(msg)
        except:
            await query.message.reply_text(msg)
            
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
            pass
        
    elif data.startswith("rate_star:"):
        stars = int(data.split(":")[1])
        user_states[user_id + 1000] = stars
        user_states[user_id] = "waiting_for_rating_text"
        try:
            await query.edit_message_text(f"لقد اخترت {stars} نجوم ⭐.\nالآن يرجى إرسال رسالة برأيك أو تقييمك للبوت:")
        except:
            pass
        
    elif data.startswith("rating_page:"):
        idx = int(data.split(":")[1])
        total = len(user_ratings)
        idx = max(0, min(idx, total - 1))
        r = user_ratings[idx]
        stars_str = "⭐" * r["stars"]
        ratings_content = (
            f"⭐ **التقييمات ({idx + 1}/{total}):**\n\n"
            f"👤 **{r['name']}** {stars_str}\n"
            f"{r['text']}"
        )
        nav_buttons = []
        if idx > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"rating_page:{idx - 1}"))
        if idx < total - 1:
            nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"rating_page:{idx + 1}"))
            
        keyboard = []
        if nav_buttons:
            keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton("➕ إضافة تقييم", callback_data="start_add_rating")])
        keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")])
        
        try:
            await query.edit_message_text(ratings_content, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass
        
    elif data.startswith("copy_key:"):
        key_to_copy = data.split(":", 1)[1]
        try:
            await query.answer(f"تم النسخ بنجاح: {key_to_copy}", show_alert=True)
        except Exception:
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
