import os
import asyncio
import subprocess
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

# عداد الطلبات الناجحة (يمكن جعله يتحدث ويحفظ في ملف لاحقاً)
successful_requests_count = 1136

# الأزرار الرئيسية أسفل الشاشة مطابقة للصورة تماماً
def get_main_keyboard():
    keyboard = [
        ["🔗 تجاوز رابط"],
        ["🌐 المواقع المدعومة", "📖 شرح البوت"],
        ["⭐ تقييم البوت", "🌍 تغيير اللغة"],
        ["📊 الطلبات الناجحة: 1136"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "مرحباً بك في بوت تجاوز الروابط 👋\n\n"
        "اختر الخدمة من القائمة:"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    if user_text == "🔗 تجاوز رابط" or user_text == "تجاوز رابط":
        await update.message.reply_text("أرسل رابط دلتا الآن (مثل: https://auth.platorelay.com/...) لأقوم باستخراج الكود لك.")
        return
        
    elif user_text == "🌐 المواقع المدعومة":
        await update.message.reply_text("الموقع المدعوم حالياً:\n- auth.platorelay.com (Delta)")
        return
        
    elif user_text == "📖 شرح البوت":
        await update.message.reply_text("فقط قم بإرسال رابط التجاوز الخاص بك، وسيقوم البوت بالتعامل مع الأداة في الخلفية وإعطائك النتيجة مباشرة.")
        return
        
    elif user_text == "⭐ تقييم البوت":
        ratings_text = (
            "⭐ **التقييمات:**\n\n"
            "👤 **Mohamed** ⭐⭐⭐⭐⭐\nكويس جدا ويسهل عليك وقت كبير\n\n"
            "👤 **معصومة بلال** ⭐⭐⭐⭐⭐\nفوللل جربووو\n\n"
            "👤 **Cristiano** ⭐⭐⭐⭐⭐\nياخي اسطوره الي اخترع هادا البوت"
        )
        keyboard = [[InlineKeyboardButton("➕ إضافة تقييم", callback_data="add_rating")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]]
        await update.message.reply_text(ratings_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return
        
    elif user_text == "🌍 تغيير اللغة":
        lang_text = "👇 الرجاء اختيار اللغة 👇"
        keyboard = [
            [InlineKeyboardButton("🇮🇶 العربية", callback_data="lang_ar"),
             InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
        ]
        await update.message.reply_text(lang_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
        
    elif "الطلبات الناجحة" in user_text:
        await update.message.reply_text(f"📊 عدد الطلبات الناجحة عبر البوت حتى الآن هو: {successful_requests_count} طلب.")
        return

    # معالجة روابط دلتا المرسلة
    if "platorelay.com" in user_text or "d=" in user_text:
        status_msg = await update.message.reply_text("⏳ جارٍ حل الرابط واستخراج الكود، انتظر قليلاً...")
        
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
            
            if process.returncode ==0:
                global successful_requests_count
                successful_requests_count += 1
                
                # استخراج الرابط أو الكود الناتج
                solved_link = ""
                for line in output_text.splitlines():
                    if "FREE_" in line or "http" in line or "KEY" in line:
                        solved_link = line.strip()
                        break
                if not solved_link:
                    solved_link = output_text[-100:]

                # تنسيق شكل رسالة النتيجة مثل الصورة المطلوبة تماماً
                result_message = (
                    f"🔗 {solved_link}\n\n"
                    f"⏳ الوقت المستغرق: {elapsed_time:.2f} ثانية\n\n"
                    f"🔔:\n"
                    f"اضغط على الرابط أعلاه للنسخ السريع، أو استخدم زر النسخ المخصص بالأسفل."
                )

                keyboard = [
                    [InlineKeyboardButton("📋 نسخ الرابط", callback_data="copy_link")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
                ]
                
                await status_msg.delete()
                await update.message.reply_text(result_message, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await status_msg.edit_text("❌ فشل في حل الرابط، يجدر المحاولة لاحقاً أو التأكد من صلاحية الرابط.")
                
        except Exception as e:
            await status_msg.edit_text(f"حدث خطأ: {str(e)}")
    else:
        await update.message.reply_text("يرجى اختيار أمر من القائمة أو إرسال رابط صحيح.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_menu":
        await query.message.delete()
        await query.message.reply_text("القائمة الرئيسية:", reply_markup=get_main_keyboard())
    elif query.data == "lang_ar":
        await query.edit_message_text("تم تغيير اللغة إلى العربية بنجاح 🇮🇶")
    elif query.data == "lang_en":
        await query.edit_message_text("Language changed to English successfully 🇺🇸")
    elif query.data == "add_rating":
        await query.message.reply_text("لإضافة تقييمك، يرجى كتابة رسالة بالتقييم لإرسالها للمطور.")

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
    
    print("Bot is running with full custom UI...")
    app.run_polling()

if __name__ == "__main__":
    main()
