import telebot
import subprocess
import time

TOKEN = "8966597040:AAFRs5K7XJD5bXToG4m3IqVSHy6gw7BgSDQ"
bot = telebot.TeleBot(TOKEN)

print("البوت يعمل الآن وجاهز للاستقبال ومعالجة الروابط...")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "أهلاً بك في بوت تجاوز روابط PlatoBoost! 🚀\nأرسل لي الرابط وسأقوم بحله واستخراج النتيجة فوراً.")
    except Exception as e:
        print(f"خطأ في start: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text.strip()
    
    if user_text.startswith("http://") or user_text.startswith("https://"):
        msg = bot.reply_to(message, "⏳ جاري تشغيل أداة التجاوز والحل، قد يستغرق ذلك بضع ثوانٍ...")
        
        try:
            # استدعاء ملف main.py محلياً لتنفيذ الحل على الرابط المرسل
            process = subprocess.run(
                ["python", "main.py", user_text],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            
            output = process.stdout.strip()
            error_output = process.stderr.strip()
            
            if output:
                # إرسال النتيجة المستخرجة
                bot.edit_message_text(f"✅ تم الحل بنجاح النتيجة:\n\n{output}", chat_id=message.chat.id, message_id=msg.message_id)
            elif error_output:
                bot.edit_message_text(f"⚠️ حدث تنبيه من الأداة:\n{error_output[:300]}", chat_id=message.chat.id, message_id=msg.message_id)
            else:
                bot.edit_message_text("❌ لم تقم الأداة بإرجاع أي نتيجة.", chat_id=message.chat.id, message_id=msg.message_id)
                
        except subprocess.TimeoutExpired:
            bot.edit_message_text("❌ انتهت مهلة الانتظار (Timeout)، استغرقت عملية الحل وقتاً طويلاً.", chat_id=message.chat.id, message_id=msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ حدث خطأ أثناء تشغيل أداة الحل: {str(e)}", chat_id=message.chat.id, message_id=msg.message_id)
    else:
        bot.reply_to(message, "يرجى إرسال رابط صحيح يبدأ بـ http:// أو https://")

while True:
    try:
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"إعادة اتصال تلقائي بعد الخطأ: {e}")
        time.sleep(3)
