import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8815004150:AAEO-paQOWRnQ88w_tSKHyG71TA37ndF1xg"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("أهلاً بك يا بطل! 🚀\nأرسل لي أي رابط مختصر (مثل LootLabs)، وسأقوم بتخطيه لك فوراً.")

@dp.message()
async def handle_links(message: types.Message):
    user_text = message.text
    
    if user_text and ("http://" in user_text or "https://" in user_text):
        sent_msg = await message.answer("⏳ جاري تخطي الرابط، ظر لحظات...")
        
        try:
            target_url = user_text.strip()
            
            # استخدام خدمة API عامة ومجانية لتخطي الروابط المختصرة مباشرة
            bypass_api = f"https://api.bypass.vip/bypass?url={target_url}"
            
            response = requests.get(bypass_api, timeout=30)
            bypassed_link = None
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 200 or data.get("success"):
                    bypassed_link = data.get("result") or data.get("destination")
                else:
                    bypassed_link = data.get("msg") or data.get("message")

            # محاولة بديلة إذا لم تنجح الأولى
            if not bypassed_link or "http" not in str(bypassed_link):
                alt_api = f"https://api.bypass.bot/api/router?url={target_url}"
                alt_res = requests.get(alt_api, timeout=30)
                if alt_res.status_code == 200:
                    alt_data = alt_res.json()
                    bypassed_link = alt_data.get("destination") or alt_data.get("result")

            if bypassed_link and "http" in str(bypassed_link):
                await bot.edit_message_text(
                    text=f"✅ **تم تخطي الرابط بنجاح!**\n\nالرابط المباشر:\n`{bypassed_link}`",
                    chat_id=message.chat.id,
                    message_id=sent_msg.message_id,
                    parse_mode="Markdown"
                )
            else:
                await bot.edit_message_text(
                    text=f"❌ عذراً، لم يتمكن البوت من تخطي هذا الرابط حالياً.\nالرد من الخادم: {bypassed_link}",
                    chat_id=message.chat.id,
                    message_id=sent_msg.message_id
                )
                
        except Exception as e:
            await bot.edit_message_text(
                text=f"❌ حدث خطأ أثناء الاتصال: {str(e)}",
                chat_id=message.chat.id,
                message_id=sent_msg.message_id
            )
    else:
        await message.answer("الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
