وتجاوز os
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# توكن البوت الخاص بك
TOKEN = "8512256766:AAGmFS1y0JnmACIb42bDGREbZ-gcfPliev4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# القائمة الرئيسية مع الأزرار التفاعلية
def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 فحصوتجاوز رابط", callback_data="bypass_link")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ])
    return keyboard

@dp.message(Command("start"))
async def send_welcome(message: Message):
    welcome_text = (
        "مرحباً بك في بوت تجاوز الروابط الذكي!\n\n"
        "أرسل لي أي رابط (مثل Boosty أو غيره) وسأحاول استخراج الرابط الأصلي، أو استخدم الأزرار أدناه:"
    )
    await message.reply(welcome_text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لتجاوز الروابط الذكية وحماية Cloudflare واستخراج الروابط الأصلية بكفاءة.",
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
        processing_msg = await message.reply("جارٍ معالجة الرابط وتجاوز الحماية...")
        
        try:
            # محاكاة تصفح حقيقي لتخطي حواجز الحماية البسيطة و الـ Cloudflare التوجيهية
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            # تتبع الروابط الموجهة (Redirects) واستخراج الرابط النهائي
            response = requests.get(text, headers=headers, allow_redirects=True, timeout=15)
            final_url = response.url
            
            if final_url != text:
                result_text = (
                    f"✅ **تم تجاوز الرابط بنجاح!**\n\n"
                    f"🔗 **الرابط الأصلي:**\n{final_url}"
                )
            else:
                # محاولة فحص إضافية إذا لم يحدث توجيه مباشر
                result_text = (
                    f"🔗 **رابط الفحص النهائي:**\n{final_url}\n\n"
                    f"⚠️ ملاحظة: إذا كان الموقع يحميه نظام Cloudflare متقدم يتطلب JavaScript، فقد يحتاج السيرفر لمتصفح وهمي (Selenium/Playwright)."
                )
                
            await processing_msg.edit_text(result_text)
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء محاولة تجاوز الرابط:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
