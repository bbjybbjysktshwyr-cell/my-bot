import asyncio
import json
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ضع توكن البوت الخاص بك هنا
TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 مرحباً بك في بوت تجاوز الروابط\n\n"
        "أرسل رابط Linkvertise وسأقوم بتجاوزه لك فوراً!"
    )

@dp.message(lambda message: message.text and "linkvertise" in message.text.lower())
async def handle_linkvertise(message: types.Message):
    user_text = message.text.strip()
    processing_msg = await message.answer("⏳ جاري تجاوز الرابط، يرجى الانتظار...")
    
    try:
        # استدعاء أداة linkvertisebypass محلياً عبر سطر الأوامر (CLI)
        process = await asyncio.create_subprocess_exec(
            "python", "-m", "linkvertisebypass.cli", user_text,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        output_text = stdout.decode('utf-8').strip()
        
        extracted_result = ""
        try:
            data = json.loads(output_text)
            if isinstance(data, dict):
                extracted_result = data.get("url") or data.get("destination") or data.get("result") or str(data)
        except json.JSONDecodeError:
            # البحث عن رابط مباشر في المخرجات إن لم تكن بصيغة JSON
            for line in output_text.splitlines():
                if "http://" in line or "https://" in line:
                    extracted_result = line.strip()
                    break
                    
        if extracted_result and "http" in extracted_result:
            await processing_msg.edit_text(f"✅ تم التجاوز بنجاح:\n\n{extracted_result}")
        else:
            error_details = output_text[-200:] if output_text else stderr.decode('utf-8')[-200:]
            await processing_msg.edit_text(f"❌ فشل في تجاوز الرابط!\nالتفاصيل: {error_details}")
            
    except Exception as e:
        await processing_msg.edit_text(f"❌ حدث خطأ أثناء المعالجة: {str(e)}")

async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
