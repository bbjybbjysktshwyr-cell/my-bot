import os
import sys
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

# استدعاء ملفاتك والأدوات الموجودة في المستودع لديك
try:
    import main as bypass_tool  # استدعاء ملف الفك الأساسي لديك
except ImportError:
    bypass_tool = None

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

successful_requests_count = 1136
user_languages = {}
user_ratings = [
    {"name": "Mohamed", "stars": 5, "text": "كويس جدا ويسهل عليك وقت كبير"},
    {"name": "معصومة بلال", "stars": 5, "text": "فوللل جربووو"},
    {"name": "Cristiano", "stars": 5, "text": "ياخي اسطوره الي اخترع هادا البوت"}
]
user_states = {}
last_results = {}

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

async def run_local_tools(url: str) -> str:
    """تشغيل الأدوات المحلية الموجودة في مستودعك لاستخراج الرابط"""
    try:
        # تشغيل ملف main.py محلياً عبر أمر بايثون داخلي يمرر الرابط
        cmd = [sys.executable, "main.py", url]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        output = stdout.decode('utf-8', errors='ignore').strip()
        
        # البحث عن رابط ناتج صالح داخل مخرجات الأدوات
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("http://") or line.startswith("https://"):
                if url not in line:  # التأكد أنه ليس الرابط الأصلي المرسل
                    return line
                    
        # إذا لم يطبع الرابط مباشرة، نرجع آخر مخرجات الأداة إذا كانت مفتاحاً أو نصاً صالحاً
        if output and len(output) > 5 and "http" not in output:
            return output
            
    except Exception as e:
        print(f"Tool Execution Error: {e}")
        
    return ""

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
        wait_msg = "⏳ جارٍ تشغيل الأدوات واستخراج النتيجة..."
        status_msg = await update.message.reply_text(wait_msg)
        
        start_time = asyncio.get_event_loop().time()
        
        # استدعاء الأدوات المحلية المرفوعة في المستودع
        extracted_result = await run_local_tools(user_text)
            
        elapsed_time = asyncio.get_event_loop().time() - start_time
        
        try:
            await status_msg.delete()
        except:
            pass

        if extracted_result:
            successful_requests_count += 1
            last_results[user_id] = extracted_result

            result_message = (
                f"✅ **النتيجة المستخرجة بواسطة أدواتك:**\n`{extracted_result}`\n\n"
                f"⏳ الوقت المستغرق: {elapsed_time:.2f} ثانية"
            )
            keyboard = [
                [InlineKeyboardButton("📋 نسخ النتيجة", callback_data="copy_res")],
                [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_menu")]
            ]
            await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            fail_message = "❌ عذراً، لم تتمكن الأدوات المحلية من استخراج النتيجة أو أن الرابط يتطلب تدخلاً."
            keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_menu")]]
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
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"r_prev:{index - 1}"))
    if index < total - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"r_next:{index + 1}"))
        
    keyboard = []
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("➕ إضافة تقييم", callback_data="r_add")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_menu")])
    
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
    
    if data == "back_menu":
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
            
    elif data == "r_add":
        keyboard = [
            [InlineKeyboardButton("⭐", callback_data="star:1"),
             InlineKeyboardButton("⭐⭐", callback_data="star:2"),
             InlineKeyboardButton("⭐⭐⭐", callback_data="star:3")],
            [InlineKeyboardButton("⭐⭐⭐⭐", callback_data="star:4"),
             InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="star:5")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="r_back")]
        ]
        try:
            await query.edit_message_text("اختر عدد النجوم لتقييم البوت:", reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass
        
    elif data.startswith("star:"):
        stars = int(data.split(":")[1])
        user_states[user_id + 1000] = stars
        user_states[user_id] = "waiting_for_rating_text"
        try:
            await query.edit_message_text(f"لقد اخترت {stars} نجوم ⭐.\nالآن يرجى إرسال رسالة برأيك أو تقييمك للبوت:")
        except:
            pass
            
    elif data == "r_back":
        await show_ratings_page_message(query.message, 0, lang)
        try:
            await query.message.delete()
        except:
            pass
        
    elif data.startswith("r_prev:") or data.startswith("r_next:"):
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
            nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"r_prev:{idx - 1}"))
        if idx < total - 1:
            nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"r_next:{idx + 1}"))
            
        keyboard = []
        if nav_buttons:
            keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton("➕ إضافة تقييم", callback_data="r_add")])
        keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_menu")])
        
        try:
            await query.edit_message_text(ratings_content, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass
        
    elif data == "copy_res":
        real_result = last_results.get(user_id, "تم النسخ بنجاح!")
        try:
            await query.answer(f"النتيجة: {real_result[:50]}", show_alert=True)
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
    
    print("Bot is running and executing local tools from repository...")
    app.run_polling()

if __name__ == "__main__":
    main()
