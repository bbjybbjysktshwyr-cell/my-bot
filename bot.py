import telebot
import requests
import time

TOKEN = "8966597040:AAFRs5K7XJD5bXToG4m3IqVSHy6gw7BgSDQ"
bot = telebot.TeleBot(TOKEN)

print("البوت يعمل الآن وجاهز للاستقبال...")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "أهلاً بك! البوت متصل ويعمل بنجاح 🚀")
        print("تم الرد على أمر /start بنجاح")
    except Exception as e:
        print(f"خطأ: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text.strip()
    print(f"تم استلام رسالة: {user_text}")
    if user_text.startswith("http://") or user_text.startswith("https://"):
        msg = bot.reply_to(message, "⏳ جاري معالجة الرابط...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(user_text, headers=headers, allow_redirects=True, timeout=10)
            bot.edit_message_text(f"✅ النتيجة:\n{response.url}", chat_id=message.chat.id, message_id=msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ حدث خطأ: {str(e)}", chat_id=message.chat.id, message_id=msg.message_id)
    else:
        bot.reply_to(message, f"أهلاً بك! تم استلام رسالتك: {user_text}")

# حلقة تشغيل آمنة تعيد الاتصال تلقائياً إذا توقف البوت
while True:
    try:
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"حدث انقطاع في الاتصال: {e}, جاري إعادة المحاولة خلال 5 ثوانٍ...")
        time.sleep(5)
