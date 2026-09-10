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
    await message.answer("أهلاً بك! أرسل لي الرابط المختصر وسأقوم بمحاولة تخطيه لك.")

@dp.message()
async def handle_links(message: types.Message):
    user_text = message.text
    
    if user_text and ("http://" in user_text or "https://" in user_text):
        sent_msg = await message.answer("⏳ جاري محاولة تخطي الرابط والانتظار...")
        
        try:
            target_url = user_text.strip()
            
            # رابط الـ API الخاص بموقع التخطي
            api_url = f"https://keybypass.net/api/bypass?url={target_url}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://keybypass.net/"
            }
            
            response = requests.get(api_url, headers=headers, timeout=30)
            
            bypassed_link = None
            if response.status_code == 200:
                try:
                    res_data = response.json()
                    bypassed_link = res_data.get("destination") or res_data.get("url") or res_data.get("result")
                except:
                    bypassed_link = response.text.strip()

            if bypassed_link and "http" in bypassed_link:
                await bot.edit_message_text(
                    text=f"✅ **التخطي بنجاح!**\n\nالرابط المباشر:\n`{bypassed_link}`",
                    chat_id=message.chat.id,
                    message_id=sent_msg.message_id,
                    parse_mode="Markdown"
                )
            else:
                await bot.edit_message_text(
                    text="❌ عذراً، الموقع يتطلب انتظار وقت أو تجاوز حماية لا يمكن تجاوزه بالطلب المباشر.",
                    chat_id=message.chat.id,
                    message_id=sent_msg.message_id
                )
                
        except Exception as e:
            await bot.edit_message_text(
                text=f"❌ حدث خطأ: {str(e)}",
                chat_id=message.chat.id,
                message_id=sent_msg.message_id
            )
    else:
        await message.answer("الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
