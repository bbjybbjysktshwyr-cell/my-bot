import os
import telebot
from shadows_v2 import getDest  # استدعية دالة التجاوز من الملف الثاني

# ضع توكن بوت التيليجرام الخاص بك هنا أو عبر متغيرات البيئة
TOKEN = os.getenv("BOT_TOKEN", "8618789887:AAGKxnDN6a0ulOS9aLyB1HnuNygukFsIVHs")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك! أرسل لي رابط LootLabs أو Loot-Link وسأقوم بتجاوزه لك فوراً.")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    
    # التأكد من أن الإرسال عبارة عن رابط
    if url.startswith("http://") or url.startswith("https://"):
        msg = bot.reply_to(message, "⏳ جاري معالجة الرابط وتجاوزه، يرجى الانتظار...")
        try:
            # استدعاء دالة التجاوز من ملف shadows_v2.py
            result = getDest(url)
            bot.edit_message_text(f"✅ **تم التجاوز بنجاح!**\n\nرابط الوجهة:\n{result}", 
                                  chat_id=message.chat.id, 
                                  message_id=msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ حدث خطأ أثناء التجاوز:\n`{str(e)}`", 
                                  chat_id=message.chat.id, 
                                  message_id=msg.message_id, 
                                  parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ يرجى إرسال رابط صحيح يبدأ بـ http:// أو https://")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
