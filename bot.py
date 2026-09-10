import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8512256766:AAGmFS1y0JnmACIb42bDGREbZ-gcfPliev4"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("أهلاً بك! أرسل لي الرابط المختصر وسأقوم بولة تخطيه.")

@dp.message()
async def handle_links(message: types.Message):
    user_text = message.text
    
    if user_text and ("http://" in user_text or "https://" in user_text):
        sent_msg = await message.answer("⏳ جاري معالجة الرابط، انتظر قليلاً...")
        
        try:
            target_url = user_text.strip()
            api_url = f"https://keybypass.net/api/v1/bypass"
            
            payload = {
                "url": target_url
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36",
                "Referer": "https://keybypass.net/",
                "Content-Type": "application/json"
            }
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            
            bypassed_link = None
            if response.status_code == 200:
                try:
                    res_data = response.json()
                    bypassed_link = res_data.get("link") or res_data.get("url") or res_data.get("destination") or res_data.get("result")
                except:
                    bypassed_link = response.text.strip()
            else:
                get_response = requests.get(f"https://keybypass.net/api?url={target_url}", headers=headers, timeout=30)
                if get_response.status_code == 200:
                    try:
                        res_data = get_response.json()
                        bypassed_link = res_data.get("link") or res_data.get("url") or res_data.get("destination") or res_data.get("result")
                    except:
                        bypassed_link = get_response.text.strip()

            if bypassed_link and "http" in bypassed_link:
                await bot.edit_message_text(
                    text=f"✅ **تم التخطي بنجاح!**\n\nالرابط المباشر:\n`{bypassed_link}`",
                    chat_id=message.chat.id,
                    message_id=sent_msg.message_id,
                    parse_mode="Markdown"
                )
            else:
                await bot.edit_message_text(
                    text="❌ عذراً، الموقع يتطلب تفاعل متصفح حقيقي.",
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
        await message.answer("الرجاء إرسال رابط صحيح.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
