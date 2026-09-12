import telebot
import subprocess
import time

TOKEN = "8966597040:AAFRs5K7XJD5bXToG4m3IqVSHy6gw7BgSDQ"
bot = telebot.TeleBot(TOKEN)

print("البوت يعمل الآن وجاهز للاستقبال ومعالجة الروابط...")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "أهلاً بكسل الرابط لنرى مخرجات الأداة.")
    except Exception as e:
        print(f"خطأ في start: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text.strip()
    
    if user_text.startswith("http://") or user_text.startswith("https://"):
        msg = bot.reply_to(message, "⏳ جاري تنفيذ الأداة...")
        
        try:
            # تشغيل ملف main.py وإرسال الرابط كبارامتر
            process = subprocess.run(
                ["python", "main.py", user_text],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            
            output = process.stdout.strip()
            error_output = process.stderr.strip()
            
            # طباعة ما تم إرجاعه تماماً في التيليجرام لنفهم سبب المشكلة
            result_msg = f"📤 الناتج من الأداة:\n{output if output else 'فارغ'}"
            if error_output:
                result_msg += f"\n\n⚠️ الأخطاء:\n{error_output}"
                
            bot.edit_message_text(result_msg[:4000], chat_id=message.chat.id, message_id=msg.message_id)
                
        except Exception as e:
            bot.edit_message_text(f"❌ حدث خطأ برمجي: {str(e)}", chat_id=message.chat.id, message_id=msg.message_id)
    else:
        bot.reply_to(message, "أرسل رابطاً صحيحاً.")

while True:
    try:
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"إعادة اتصال: {e}")
        time.sleep(3)
