import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '8860565104:AAEVEX4ODFumP981Sto89sCZZmOe7MSHtzU'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً بك في بوت استخراج مفاتيح دلتا! 🚀\nأرسل رابط دلتا الآن وسأقوم بمعالجته واستخراج المفتاح لك.")

@dp.message_handler(lambda message: "platorelay.com" in message.text or "delta" in message.text.lower())
async def handle_delta_link(message: types.Message):
    user_link = message.text.strip()
    processing_msg = await message.reply("⏳ جاري تخطي الرابط واستخراج المفتاح، يرجى الانتظار...")
    
    try:
        # ضع هنا رابط السيرفر الخاص بك أو الأداة البرمجية الحقيقية التي تتجاوز الرابط
        # أو استخدم الكود الخاص بتجاوز دلتا مباشرة هنا:
        
        async with aiohttp.ClientSession() as session:
            # مثال على طلب الـ API الفعلي لتجاوز الرابط (قم بتعديل الرابط أدناه بالرابط الصحيح للأداة إن وجدت)
            bypass_api = f"https://api.allorigins.win/get?url={user_link}" # مثال فقط للاتصال
            async with session.get(bypass_api) as response:
                if response.status == 200:
                    # هنا يتم معالجة النتيجة واستخراج المفتاح الحقيقي
                    # كمثال تجريبي، نضع صيغة النجاح:
                    extracted_key = "DELTA-KEY-EXAMPLE-12345" 
                    
                    await bot.edit_message_text(
                        text=f"✅ تم استخراج المفتاح بنجاح:\n`{extracted_key}`",
                        chat_id=message.chat.id,
                        message_id=processing_msg.message_id,
                        parse_mode="Markdown"
                    )
                else:
                    await bot.edit_message_text(
                        text="❌ فشل في تجاوز الرابط، تأكد أن الرابط صالح.",
                        chat_id=message.chat.id,
                        message_id=processing_msg.message_id
                    )
    except Exception as e:
        await bot.edit_message_text(
            text=f"❌ حدث خطأ:\n`{str(e)}`",
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            parse_mode="Markdown"
        )

if __name__ == '__main__':
    print("🤖 بوت تيليجرام يعمل الآن بكفاءة...")
    executor.start_polling(dp, skip_updates=True)
