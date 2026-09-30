import os
import telebot
from main import solve_chain
import auth_client as AUTH

# وضع توكن البوت الخاص بك هنا
TOKEN = "8234621209:AAGboD954ect3e8WCrtPRCVT5P5e0BeBVAk"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك في بوت تخطي روابط دلتا!\nأرسل لي رابط دلتا أو الـ Ticket وسأقوم"
      " بمحاولة استخراج المفتاح لك.",
  )


@bot.message_handler(func=lambda message: True)
def handle_link(message):
  user_input = message.text.strip()

  # التأكد من أن الإدخال يحتوي على رابط أو تكت صالح
  if (
      "platorelay.com" in user_input
      or "delta" in user_input
      or len(user_input) > 50
  ):
    msg = bot.reply_to(
        message, "🔄 جاري معالجة الرابط وتخطي الحماية، يرجى الانتظار..."
    )

    try:
      # استخراج الـ ticket باستخدام دوال auth_client الموجودة لديك
      ticket = AUTH.extract_ticket(user_input)

      # استدعاء دالة التخطي الأساسية الموجودة في ملف main.py
      key, timer = solve_chain(ticket, verbose=False, max_rounds=3, session=None)

      if key:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=f"✅ **تم التخطي بنجاح!**\n\n🔑 **المفتاح:**\n`{key}`",
            parse_mode="Markdown",
        )
      else:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=(
                "❌ فشل في استخراج المفتاح. قد يكون الرابط منتهي الصلاحية أو"
                " محظوراً."
            ),
        )
    except Exception as e:
      bot.edit_message_text(
          chat_id=message.chat.id,
          message_id=msg.message_id,
          text=f"⚠️ حدث خطأ أثناء المعالجة: `{str(e)}`",
          parse_mode="Markdown",
      )
  else:
    bot.reply_to(
        message, "⚠️ يرجى إرسال رابط دلتا صحيح أو تكت صالح (Ticket)."
    )


if __name__ == "__main__":
  print("البوت يعمل الآن...")
  bot.infinity_polling()
