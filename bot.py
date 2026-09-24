import asyncio
import subprocess
import sys
import aiohttp
from aiogram import Bot, Dispatcher, executor, types

# توكن البوت الخاص بك
API_TOKEN = '8860565104:AAEVEX4ODFumP981Sto89sCZZmOe7MSHtzU'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

server_process = None

def start_local_server():
    global server_process
    try:
        server_process = subprocess.Popen([sys.executable, "server.py"])
        print("🤖 تم تشغيل السيرفر المحلي بنجاح.")
    except Exception as e:
        print(f"❌ خطأ أثناء تشغيل السيرفر: {e}")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً بك في بوت استخراج مفاتيح دلتا! 🚀\nأرسل رابط دلتا الآن وسأقوم باستخراج المفتاح لك فوراً.")

@dp.message_handler(lambda message: "platorelay.com" in message.text or "delta" in message.text.lower())
async def handle_delta_link(message: types.Message):
    user_link = message.text.strip()
    
    # إرسال رسالة انتظار للمستخدم
    processing_msg = await message.reply("⏳ جاري معالجة الرابط واستخراج المفتاح، يرجى الانتظار...")
    
    try:
        # إرسال الرابط إلى السيرفر المحلي (تأكد من المنفذ البورت الصحيح للسيرفر مثل 5000 أو 8000)
        server_url = "http://127.0.0.1:5000/api" # عدل الرابط حسب مسار الـ API في سيرفرك
        
        async with aiohttp.ClientSession() as session:
            async with session.post(server_url, json={"link": user_link}) as response:
                if response.status == 200:
                    data = await response.json()
                    key = data.get("key", "لم يتم العثور على المفتاح.")
                    await bot.edit_message_text(
                        text=f"✅ تم استخراج المفتاح بنجاح:\n`{key}`",
                        chat_id=message.chat.id,
                        message_id=processing_msg.message_id,
                        parse_mode="Markdown"
                    )
                else:
                    await bot.edit_message_text(
                        text="❌ حدث خطأ من السيرفر أثناء محاولة استخراج المفتاح.",
                        chat_id=message.chat.id,
                        message_id=processing_msg.message_id
                    )
    except Exception as e:
        await bot.edit_message_text(
            text=f"❌ تعذر الاتصال بالسيرفر المحلي:\n`{str(e)}`",
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            parse_mode="Markdown"
        )

if __name__ == '__main__':
    try:
        # تشغيل السيرفر أولاً
        start_local_server()
        print("🤖 بوت تيليجرام يعمل الآن (مع السيرفر في الخلفية)...")
        executor.start_polling(dp, skip_updates=True)
    finally:
        if server_process:
            server_process.terminate()
            print("🛑 تم إيقاف السيرفر المحلي.")
