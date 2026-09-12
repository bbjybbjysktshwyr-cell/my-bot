import os
import telebot
from shadows_v2 import getDest

# توكن البوت الخاص بك
TOKEN = "8966597040:AAFRs5K7XJD5bXToG4m3IqVSHy6gw7BgSDQ"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أسل رابط LootLabs لتجربة التخطي واستخراج المفتاح.")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    
    if "lootlabs.gg" in url or "http://" in url or "https://" in url:
        msg = bot.reply_to(message, "⏳ جاري محاولة تخطي الرابط واستخراج المفتاح...")
        
        try:
            def verbose_print(text):
                print(f"[LOG]: {text}")
            
            # استدعاء دالة التخطي من shadows_v2.py
            result = getDest(url, verbose_cb=verbose_print)
            
            bot.edit_message_text(f"✅ النتيجة:\n\n`{result}`", chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")
        except Exception as e:
            bot.edit_message_text(f"❌ حدث خطأ أثناء التخطي:\n`{e}`", chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ يرجى إرسال رابط صحيح صالح للتخطي.")

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    bot.infinity_polling()
