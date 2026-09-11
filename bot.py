import os
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# توكن البوت الخاص بك
TOKEN = "8512256766:AAGmFS1y0JnmACIb42bDGREbZ-gcfPliev4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# إنشاء سكربت تجاوز الكلاود فلير
scraper = cloudscraper.create_scraper()

def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 فحص وتجاوز رابط", callback_data="bypass_link")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ])
    return keyboard

@dp.message(Command("start"))
async def send_welcome(message: Message):
    welcome_text = (
        "مرحباً بك في بوت تجاوز الروابط الذكي!\n\n"
        "أرسل لي أي رابط (مثل Boosty) وسأقوم بتجاوز الحماية واستخراج الرابط الأصلي:"
    )
    await message.reply(welcome_text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لتجاوز الروابط وحماية Cloudflare بكفاءة عالية.",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: Message):
    await callback.message.edit_text(
        "يرجى إرسال الرابط المطلوب تخطيه مباشرة في المحادثة."
    )

@dp.message()
async def handle_links(message: Message):
    text = message.text
    if text and text.startswith("http"):
        processing_msg = await message.reply("جارٍ تجاوز حماية Cloudflare وسحب الرابط...")
        
        try:
            # استخدام cloudscraper لتخطي حماية الكلاود فلير وجلب التوجيهات
            response = scraper.get(text, timeout=20, allow_redirects=True)
            final_url = response.url
            
            if final_url != text:
                result_text = (
                    f"✅ **تم تخطي الحماية بنجاح!**\n\n"
                    f"🔗 **الرابط الأصلي:**\n{final_url}"
                )
            else:
                result_text = (
                    f"🔗 **الرابط النهائي بعد الفحص:**\n{final_url}\n\n"
                    f"⚠️ الموقع لم يقم بإعادة التوجيه التلقائي، قد يتطلب تفاعلاً يدوياً أو أن الرابط الأصلي هو نفسه."
                )
                
            await processing_msg.edit_text(result_text)
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء تجاوز الحماية:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
