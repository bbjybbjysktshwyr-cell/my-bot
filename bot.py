import os
import re
import html
import asyncio
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "8512256766:AAGmFS1y0JnmACIb42bDGREbZ-gcfPliev4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 فحص وتجاوز رابط", callback_data="bypass_link")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ])

def get_copy_keyboard(target_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 نسخ الرابط", url=target_url)],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "مرحباً بك! أرسل رابط الاختصار وسأقوم باستخراج الرابط:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لاستخراج الروابط الأصلية وتجاوز صفحات الاختصار بدقة وسرعة.",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: Message):
    await callback.message.edit_text("يرجى إرسال الرابط مباشرة في المحادثة.")
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: Message):
    await callback.message.edit_text("أرسل الرابط المطلوب فحصه:", reply_markup=get_main_menu())
    await callback.answer()

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_links(message: Message):
    text = message.text
    if text and text.startswith("http"):
        processing_msg = await message.answer("⏳ جاري تتبع مسار الرابط واستخراج الوجهة...")
        
        extracted_url = text
        
        try:
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'android', 'desktop': False}
            )
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                "Referer": text
            }
            
            # إيقاف التتبع التلقائي لمعرفة رابط التحويل المباشر
            response = scraper.get(text, headers=headers, allow_redirects=False, timeout=10)
            
            # فحص الـ Redirect المباشر (مثل Location header)
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_target = response.headers.get("Location")
                if redirect_target:
                    extracted_url = redirect_target
            
            # إذا لم يوجد تحويل مباشر، نقوم بعمل تتبع مع السماح بالتحويلات والبحث عن link-center
            if extracted_url == text:
                response_full = scraper.get(text, headers=headers, allow_redirects=True, timeout=15)
                if response_full.history:
                    for resp in response_full.history:
                        loc = resp.headers.get("Location")
                        if loc and "link-center.net" in loc:
                            extracted_url = loc
                            break
                    if extracted_url == text and response_full.history:
                        extracted_url = response_full.history[-1].headers.get("Location", text)

            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            if clean_url == text:
                await processing_msg.edit_text(
                    "⚠️ لم يتم استخراج الرابط تلقائياً، يمكنك فتحه يدوياً:",
                    reply_markup=get_copy_keyboard(text)
                )
            else:
                result_text = (
                    f"🎉 **تم استخراج الرابط بنجاح!**\n\n"
                    f"🔗 {clean_url}\n\n"
                    f"🔔 اضغط على زر النسخ أدناه:"
                )
                await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
                
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء المعالجة:\n`{str(e)}`")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 البوت يعمل الآن بكفاءة عالية...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
