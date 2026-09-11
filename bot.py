import os
import html
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from playwright.async_api import async_playwright

# توكن البوت
TOKEN = "8512256766:AAGmFS1y0JnmACIb42bDGREbZ-gcfPliev4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 فحص وتجاوز رابط", callback_data="bypass_link")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ])
    return keyboard

def get_copy_keyboard(target_url):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 نخ الرابط", url=target_url)],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])
    return keyboard

@dp.message(Command("start"))
async def send_welcome(message: Message):
    welcome_text = (
        "مرحباً بك في بوت تجاوز الروابط الذكي!\n\n"
        "أرسل لي أي رابط وسأقوم باستخراج الرابط الأصلي بدقة:"
    )
    await message.reply(welcome_text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لتجاوز روابط الحماية واستخراج الرابط النهائي.",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: Message):
    await callback.message.edit_text(
        "يرجى إرسال الرابط المطلوب تخطيه مباشرة في المحادثة."
    )

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: Message):
    await callback.message.edit_text(
        "مرحباً بك مرة أخرى! أرسل الرابط المطلوب تجاوزه:",
        reply_markup=get_main_menu()
    )

@dp.message()
async def handle_links(message: Message):
    text = message.text
    if text and text.startswith("http"):
        processing_msg = await message.reply("⏳ جاري محاكاة المتصفح وسحب الرابط الحقيقي...")
        
        extracted_url = None
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                
                # فتح الرابط وانتظار تحميل الشبكة بالكامل
                await page.goto(text, timeout=40000, wait_until="domcontentloaded")
                
                # انتظار إضافي لضمان عمل السكربتات والعدّادات واختفاء الحماية
                await page.wait_for_timeout(6000)
                
                # البحث عن أي رابط يحتوي على link-center أو أي وجهة نهائية داخل الصفحة
                links = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
                for l in links:
                    if l and "link-center.net" in l:
                        extracted_url = l
                        break
                
                # إذا لم يوجد في الروابط، نبحث في محتوى الـ HTML كامل عن رابط الـ link-center
                if not extracted_url:
                    content = await page.content()
                    import re
                    match = re.search(r'https?://link-center\.net/[^\s<>"\']+', content)
                    if match:
                        extracted_url = match.group(0)
                
                # إذا لم نجده، نأخذ عنوان الصفحة الحالي بعد التوجيه
                if not extracted_url:
                    current_url = page.url
                    if current_url != text:
                        extracted_url = current_url
                    else:
                        extracted_url = text
                        
                await browser.close()

            clean_url = html.unescape(extracted_url)

            result_text = (
                f"🎉 **تم استخراج الرابط بنجاح!**\n\n"
                f"🔗 `{clean_url}`\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
