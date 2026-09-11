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
        [InlineKeyboardButton(text="📋 نسخ الرابط", url=target_url)],
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
        processing_msg = await message.reply("⏳ جاري فتح المتصفح وتجاوز الحماية استخراج الرابط...")
        
        extracted_url = None
        
        try:
            # تشغيل متصفح خفي (Headless Browser) عبر Playwright لتنفيذ الجافاسكريبت والوصول للرابط النهائي
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # الانتقال للرابط والانتظار حتى يتم تحميل محتوى الصفحة بالكامل
                await page.goto(text, timeout=30000, wait_until="networkidle")
                
                # إعطاء مهلة صغيرة لضمان ظهور الرابط النهائي بعد الـ Redirect أو توليده ديناميكياً
                await page.wait_for_timeout(5000)
                
                current_url = page.url
                
                # التحقق إذا كان الرابط الحالي قد تحول إلى الرابط المطلوب (مثل link-center.net)
                if "link-center.net" in current_url or "boostylink.com" not in current_url:
                    extracted_url = current_url
                else:
                    # محاولة البحث عن روابط إعادة التوجيه أو الـ href داخل أزرار التجهيز بالصفحة
                    links = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
                    for l in links:
                        if l and "link-center.net" in l:
                            extracted_url = l
                            break
                            
                    if not extracted_url:
                        extracted_url = current_url
                        
                await browser.close()
                
            if not extracted_url or extracted_url == text:
                extracted_url = text

            clean_url = html.unescape(extracted_url)

            result_text = (
                f"🎉 **تم تجاوز الرابط بنجاح!**\n\n"
                f"🔗 `{clean_url}`\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء تجاوز الرابط:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
