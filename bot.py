import logging
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
        "أرسل لي الرابط المختصر، وسأقوم بتخجلب الرابط المباشر لك فوراً."
    )

@dp.message()
async def handle_links(message: types.Message):
    user_text = message.text
    
    # التأكد من أن الرسالة عبارة عن رابط
    if user_text and ("http://" in user_text or "https://" in user_text):
        sent_msg = await message.answer("⏳ جاري تخطي الرابط عبر الموقع، انتظر قليلاً...")
        
        try:
            target_url = user_text.strip()
            
            # ==========================================
            # هنا يتم ربط الموقع أو الـ API الفعلي للتخطي
            # ضع رابط الموقع أو الـ API الخاص بك هنا:
            # ==========================================
            api_url = f"https://keybypass.net/api?url={target_url}" # (غير الرابط إذا كان يختلف حسب موقعك)
            
            response = requests.get(api_url)
            
            # محاولة جلب النتيجة من الموقع
            if response.status_code == 200:
                # إذا كان يرجع JSON:
                try:
                    data = response.json()
                    bypassed_link = data.get("result") or data.get("url") or data.get("link") or response.text
                except:
                    # إذا كان يرجع نص عادي مباشر للرابط:
                    bypassed_link = response.text.strip()
            else:
                bypassed_link = "عذراً، لم يستجب موقع التخطي بشكل صحيح."

            await bot.edit_message_text(
                text=f"✅ **تم تخطي الرابط بنجاح!**\n\nالرابط المباشر:\n`{bypassed_link}`",
                chat_id=message.chat.id,
                message_id=sent_msg.message_id,
                parse_mode="Markdown"
            )
        except Exception as e:
            await bot.edit_message_text(
                text=f"❌ حدث خطأ أثناء الاتصال بالموقع: {str(e)}",
                chat_id=message.chat.id,
                message_id=sent_msg.message_id
            )
    else:
        await message.answer("الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
