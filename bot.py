import asyncio
import subprocess
import sys
from aiogram import Bot, Dispatcher, executor, types

# ضع توكن بوتك هنا بين القوسين
API_TOKEN =  '8860565104:AAEVEX4ODFumP981Sto89sCZZmOe7MSHtzU'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

server_process = None

def start_local_server():
    global server_process
    # تشغيل السيرفر المحلي في الخلفية
    try:
        server_process = subprocess.Popen([sys.executable, "server.py"])
        print("🤖 تم تشغيل السيرفر المحلي بنجاح.")
    except Exception as e:
        print(f"❌ خطأ أثناء تشغيل السيرفر: {e}")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً بك! أرسل رابط دلتا ليتم استخراج المفتاح فوراً.")

# يمكنك إضافة كود التعامل مع روابط دلتا هنا وتوجيه الطلب للسيرفر المحلي

if __name__ == '__main__':
    try:
        # تشغيل السيرفر أولاً
        start_local_server()
        
        print("🤖 بوت تيليجرام يعمل الآن (مع السيرفر في الخلفية)...")
        # بدء تشغيل البوت بالإصدار الثاني aiogram 2.x
        executor.start_polling(dp, skip_updates=True)
        
    finally:
        # إيقاف السيرفر عند إغلاق البوت لضمان عدم بقائه يعمل في الخلفية
        if server_process:
            server_process.terminate()
            print("🛑 تم إيقاف السيرفر المحلي.")
