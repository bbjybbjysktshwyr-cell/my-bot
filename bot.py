import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, executor, types

# توكن البوت الخاص بك
API_TOKEN = '8860565104:AAEVEX4ODFumP981Sto89sCZZmOe7MSHtzU'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً بك في بوت استخراج مفاتيح دلتا المدمج! 🚀\nأرسل رابط دلتا الآن وسأقوم بمعالجته لك فوراً.")

@dp.message_handler(lambda message: "platorelay.com" in message.text or "delta" in message.text.lower())
async def handle_delta_link(message: types.Message):
    user_link = message.text.strip()
    
    # إرسال رسالة انتظار للمستخدم
    processing_msg = await message.reply("⏳ جاري معالجة الرابط واستخراج المفتاح، يرجى الانتظار...")
    
    try:
        # هنا يمكنك وضع الكود المسؤول عن جلب المفتاح مباشرة أو إرساله للرابط الخارجي (API) إذا كان مرفوعاً على الإنترنت
        # (مثال: إذا كان لديك رابط سيرفر خارجي ثابت مثل Render ضع رابطه هنا بدلاً من 127.0.0.1)
        api_url = "https://your-server-name.onrender.com/api" # استبدل هذا برابط سيرفرك الحقيقي إن وجد، أو ضع منطق التجاوز هنا مباشرة
        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json={"link": user_link}) as response:
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
                        text="❌ حدث خطأ أثناء الاتصال بخدمة استخراج المفاتيح.",
                        chat_id=message.chat.id,
                        message_id=processing_msg.message_id
                    )
    except Exception as e:
        await bot.edit_message_text(
            text=f"❌ تعذر إتمام الطلب:\n`{str(e)}`",
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            parse_mode="Markdown"
        )

if __name__ == '__main__':
    print("🤖 بوت تيليجرام المدمج يعمل الآن...")
    executor.start_polling(dp, skip_updates=True)
