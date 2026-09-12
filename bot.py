import telebot

TOKEN = "ضع_التوكن_هنا"
bot = telebot.TeleBot(TOKEN)

print("البوت بدأ بالعمل وجاري الاتصال بـ Telegram...")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"تم استلام أمر start من المستخدم: {message.chat.id}")
    bot.reply_to(message, "مرحباً! البوت متصل ويعمل بنجاح.")

bot.infinity_polling(none_stop=True)
