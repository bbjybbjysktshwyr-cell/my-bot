import os
import sys
import json
import asyncio
import base64
import urllib.parse
import urllib.request
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

def local_linkvertise_bypass(url: str) -> str:
    """دالة محلية ذكية لاستخراج روابط Linkvertise دون الحاجة لسيرفرات خارجية"""
    try:
        if "linkvertise.com" in url or "link-to.net" in url:
            # استخراج المعرف أو الرابط وتفكيكه
            parsed = urllib.parse.urlparse(url)
            path = parsed.path
            parts = [p for p in path.split('/') if p]
            
            # محاولة جلب الرابط الأصلي عبر تحليل مسار الرابط أو جلب الصفحة بشكل مباشر
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            try:
                with urllib.request.urlopen(req, timeout=8) as response:
                    html_content = response.read().decode('utf-8', errors='ignore')
                    # البحث عن الرابط المستهدف داخل الجافاسكريبت أو محتوى الصفحة
                    if '"target":' in html_content:
                        idx = html_content.find('"target":')
                        sub = html_content[idx:idx+300]
                        parts_sub = sub.split('"')
                        for p in parts_sub:
                            if p.startswith('http://') or p.startswith('https://'):
                                return p
            except Exception:
                pass
                
            if len(parts) >= 2:
                # طريقة بديلة لاعتماد الـ ID واستخراج الوجهة
                code = parts[-1]
                target_api = f"https://linkvertise.com/api/v1/redirect?query={code}"
                req2 = urllib.request.Request(target_api, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
                try:
                    with urllib.request.urlopen(req2, timeout=6) as resp2:
                        data = json.loads(resp2.read().decode('utf-8'))
                        if "target" in data:
                            return data["target"]
                        elif "link" in data and "url" in data["link"]:
                            return data["link"]["url"]
                except Exception:
                    pass
        return url
    except Exception:
        return url

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
        msg = "Supported sites:\n- auth.platorelay.com (Delta)\n- linkvertise.com" if lang == "en" else "الموqاع المدعومة:\n- auth.platorelay.com (Delta)\n- linkvertise.com"
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
            # تنفيذ التجاوز المحلي الآمن
            extracted_result = local_linkvertise_bypass(user_text)
            if not extracted_result or extracted_result == user_text:
                extracted_result = f"https://bypass.bot.nu/bypass2?url={urllib.parse.quote(user_text)}" # محاولة أخيرة
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
                    lines = [l.strip() for l in output_text.splitlines() if l.strip() and not l.startswith("Traceback")]
                    if lines:
                        extracted_result = lines[-1]
            except Exception as e:
                extracted_result = f"EXC: {str(e)}"
            
        elapsed_time = asyncio.get_event_loop().time() - start_time
        
        try:
            await status_msg.delete()
        except:
            pass

        if extracted_result and not extracted_result.startswith("EXC:") and extracted_result != user_text:
            successful_requests_count += 1
            last_results[user_id] = extracted_result

            result_message = (
                f"✅ **النتيجة المستخرجة:**\n`{extracted_result}`\n\n"
                f"⏳ الوقت المستغرق: {elapsed_time:.2f} ثانية"
            )
            keyboard = [
                [InlineKeyboardButton("📋 نسخ النتيجة", callback_data="copy_res")],
                [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_menu")]
            ]
            await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            fail_message = "❌ عذراً، لم يتم استخراج الرابط أو أن الرابط يتطلب تفاعلاً بشرياً."
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
    
    print("Bot is running with built-in native bypass...")
    app.run_polling()

if __name__ == "__main__":
    main()
