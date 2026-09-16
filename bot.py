import os
import json
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

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
    return {"successful_requests_count": 1147}

def save_data():
    data = {"successful_requests_count": successful_requests_count}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()
successful_requests_count = db["successful_requests_count"]

def get_main_keyboard():
    keyboard = [
        ["🔗 تجاوز رابط"],
        ["🌐 المواقع المدعومة", "📖 شرح البوت"],
        [f"📊 الطلبات الناجحة: {successful_requests_count}"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "مرحباً بك في بوت تجاوز الروابط 👋\n\nاضغط على زر (تجاوز رابط) أو أرسل الرابط مباشرة:"
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global successful_requests_count
    if not update.message or not update.message.text:
        return
        
    user_text = update.message.text.strip()
    
    if "تجاوز رابط" in user_text:
        await update.message.reply_text("أرسل الرابط الآن (يدعم Linkvertise و Delta):", reply_markup=get_main_keyboard())
        return
        
    elif "المواقع المدعومة" in user_text:
        msg = "المواقع المدعومة حالياً:\n- linkvertise.com\n- auth.platorelay.com (Delta)"
        await update.message.reply_text(msg, reply_markup=get_main_keyboard())
        return
        
    elif "شرح البوت" in user_text:
        msg = "فقط اضغط على (تجاوز رابط) ثم أرسل الرابط، وسيقوم البوت باستخراج النتيجة فوراً."
        await update.message.reply_text(msg, reply_markup=get_main_keyboard())
        return
        
    elif "الطلبات الناجحة" in user_text:
        msg = f"📊 عدد الطلبات الناجحة عبر البوت حتى الآن: {successful_requests_count}"
        await update.message.reply_text(msg, reply_markup=get_main_keyboard())
        return

    if "http://" in user_text or "https://" in user_text:
        wait_msg = "⏳ جارٍ معالجة الرابط واستخراج النتيجة، انتظر قليلاً..."
        status_msg = await update.message.reply_text(wait_msg)
        
        start_time = asyncio.get_event_loop().time()
        extracted_result = ""
        
        try:
            loop = asyncio.get_running_loop()
            if "platorelay.com" in user_text or "delta" in user_text.lower():
                process = await asyncio.create_subprocess_exec(
                    "python", "main.py", user_text,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                output_text = stdout.decode('utf-8', errors='ignore').strip()
                
                for line in output_text.splitlines():
                    if "http://" in line or "https://" in line or "FREE_" in line or "key" in line.lower():
                        if user_text not in line and "127.0.0.1" not in line:
                            extracted_result = line.strip()
                            break
                if not extracted_result:
                    extracted_result = output_text
            else:
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
                    extracted_result = "Linkvertise module not loaded."
        except Exception as ex:
            extracted_result = str(ex)

        elapsed_time = asyncio.get_event_loop().time() - start_time
        
        try:
            await status_msg.delete()
        except:
            pass

        res_lower = extracted_result.lower()
        if extracted_result and "traceback" not in res_lower and len(extracted_result) > 5:
            successful_requests_count += 1
            save_data()
            
            result_message = (
                f"✅ **تم تجاوز الرابط بنجاح:**\n\n"
                f"`{extracted_result}`\n\n"
                f"⏳ الوقت المستغرق: {elapsed_time:.2f} ثانية"
            )
            await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=get_main_keyboard())
        else:
            fail_message = f"❌ فشل في تجاوز الرابط!\n\n`{extracted_result}`"
            await update.message.reply_text(fail_message, parse_mode="Markdown", reply_markup=get_main_keyboard())
    else:
        await update.message.reply_text("يرجى إرسال رابط صحيح يبدأ بـ http:// أو https://", reply_markup=get_main_keyboard())

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
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running perfectly...")
    app.run_polling()

if __name__ == "__main__":
    main()