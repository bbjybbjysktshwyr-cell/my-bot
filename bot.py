import os
import asyncio
import subprocess
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = "8975068395:AAFD_ups14mfcBbopumiZt7NCxzXaxmwC7s"

# قائمة الأزرار الرئيسية أسفل الشاشة
MAIN_MENU_KEYBOARD = [
    ["🔗 تجاوز رابط"],
    ["🌐 المواقع المدعومة", "📖 شرح البوت"],
    ["⭐ تقييم البوت", "🌍 تغيير اللغة"],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
    await update.message.reply_text(
        "مرحباً بك في بوت تجاوز الروابط 👋\n\nاختر الخدمة من القائمة:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # التعامل مع أزرار القائمة
    if user_text == "🔗 تجاوز رابط":
        await update.message.reply_text("أرسل رابط دلتا الآن (مثل: https://auth.platorelay.com/...) لأقوم باستخراج الكود لك.")
        return
    elif user_text == "🌐 المواقع المدعومة":
        await update.message.reply_text("المواقع المدعومة حالياً: Delta / Platorelay")
        return
    elif user_text == "📖 شرح البوت":
        await update.message.reply_text("فقط قم بإرسال رابط التجاوز وسيقوم البوت بحله واستخراج المفتاح تلقائياً.")
        return
    elif user_text == "⭐ تقييم البوت":
        await update.message.reply_text("شكراً لدعمك! يمكنك تقييم البوت عبر مراسلة المطور.")
        return
    elif user_text == "🌍 تغيير اللغة":
        await update.message.reply_text("اللغة الحالية: العربية 🇮🇶")
        return

    # إذا كان النص المصدَر رابط دلتا
    if "platorelay.com" in user_text or "d=" in user_text:
        status_msg = await update.message.reply_text("⏳ جارٍ حل الرابط واستخراج الكود، انتظر قليلاً...")
        
        try:
            process = await asyncio.create_subprocess_exec(
                "python", "main.py", user_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            output_text = stdout.decode('utf-8')
            
            if process.returncode == 0:
                # استخراج الكود (KEY) فقط من بين النصوص الطويلة لتكون الرسالة نظيفة
                key_line = ""
                for line in output_text.splitlines():
                    if "FREE_" in line or "KEY" in line:
                        key_line = line.strip()
                        break
                
                # إذا لم يجد مفتاحاً بكلمة مفتاحية، يأخذ السطر المناسب
                clean_key = key_line if key_line else "تم استخراج الكود بنجاح"

                # زر تفاعلي لنسخ الرابط أو العودة
                keyboard = [
                    [InlineKeyboardButton("📋 نسخ الكود / الرابط", callback_data="copy")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                result_message = (
                    f"✅ **تم تجاوز الرابط بنجاح!**\n\n"
                    f"🔑 **الكود:**\n`{clean_key}`\n\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🚀 تم التجاوز بواسطة بوتك الخاص"
                )
                
                await status_msg.delete()
                await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=reply_markup)
            else:
                await status_msg.edit_text("❌ فشل في استخراج الكود، قد يكون الرابط منتهي الصلاحية أو أن الموقع تحت الصيانة.")
                
        except Exception as e:
            await status_msg.edit_text(f"حدث خطأ تقني: {str(e)}")
    else:
        await update.message.reply_text("يرجى اختيار أمر من القائمة أو إرسال رابط صحيح.")

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
    
    print("Bot is running with new UI...")
    app.run_polling()

if __name__ == "__main__":
    main()
