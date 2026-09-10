import logging
import aiohttp
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# التوكن الخاص بك
TOKEN = "8815004150:AAEO-paQOWRnQ88w_tSKHyG71TA37ndF1xg"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "أهلاً بك يا بطل! 🚀\n"
        "أرسل لي أي رابط مختصر، وسأقوم بمحاولة تخطيه وإرجاع الرابط المباشر لك فوراً."
    )

@dp.message()
async def handle_links(message: types.Message):
    user_text = message.text
    
    # التأكد من أن الرسالة عبارة عن رابط
    if user_text and ("http://" in user_text or "https://" in user_text):
        sent_msg = await message.answer("⏳ جاري تخطي الرابط، يرجى الانتظار قليلاً...")
        
        try:
            target_url = user_text.strip()
            
            # مثال لطلب API التخطي (يمكنك تعديل الرابط حسب الـ API الخاص بـ keybypass.net إذا وجد)
            # api_url = f"https://keybypass.net/api?url={target_url}"
            # response = requests.get(api_url).json()
            # bypassed_link = response.get("result", target_url)
            
            # الرابط التجريبي حالياً لحين ربط الـ API الفعلي:
            bypassed_link = f"https://example.com/direct?url={target_url}"
            
            await bot.edit_message_text(
                text=f"✅ **تم تخطي الرابط بنجاح!**\n\nالرابط المباشر:\n`{bypassed_link}`",
                chat_id=message.chat.id,
                message_id=sent_msg.message_id,
                parse_mode="Markdown"
            )
        except Exception as e:
            await bot.edit_message_text(
                text=f"❌ حدث خطأ أثناء محاولة تخطي الرابط: {str(e)}",
                chat_id=message.chat.id,
                message_id=sent_msg.message_id
            )
    else:
        await message.answer("الرجاء إرسال رابط صحيح يبدأ بـ http أو https لكي أتمكن من تخطيه.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
