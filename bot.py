import telebot
import requests

TOKEN = "8966597040:AAFRs5K7XJD5bXToG4m3IqVSHy6gw7BgSDQ"
bot = telebot.TeleBot(TOKEN)

print("البوت بدأ بالعمل وجاري الاتصال بـ Telegram...")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت تجاوز الروابط المختصرة! 🚀\nأرسل لي أي رابط مختصر (مثل boostylink أو link-center) وسأحاول تجاوزه لك فوراً.")

@bot.message_handler(func=lambda message: True)
def handle_links(message):
    url = message.text.strip()
    
    # التحقق من أن الرسالة عبارة عن رابط
    if url.startswith("http://") or url.startswith("https://"):
        msg = bot.reply_to(message, "⏳ جاري الفحص وتجاوز الحماية...")
        
        try:
            # منطق تجاوز الروابط (يمكنك ربط خوارزمية التجاوز الخاصة بك هنا)
            # كمثال تجريبي، سنقوم بإرسال طلب لمعرفة الرابط النهائي أو محاكاة التجاوز
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
            final_url = response.url
            
            if final_url != url:
                bot.edit_message_text(f"✅ تم تجاوز الرابط بنجاح!\n\n🔗 الرابط الأصلي:\n{final_url}", chat_id=message.chat.id, message_id=msg.message_id)
            else:
                bot.edit_message_text("⚠️ لم يتم العثور على توجيه تلقائي، قد يحتاج الرابط لمعالجة خاصة.", chat_id=message.chat.id, message_id=msg.message_id)
                
        except Exception as e:
            bot.edit_message_text(f"❌ حدث خطأ أثناء محاولة تجاوز الرابط:\n{str(e)}", chat_id=message.chat.id, message_id=msg.message_id)
    else:
        bot.reply_to(message, "يرجى إرسال رابط صحيح يبدأ بـ http:// أو https://")

bot.infinity_polling(none_stop=True)
