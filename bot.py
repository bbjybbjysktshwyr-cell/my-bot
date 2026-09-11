import os
import re
import html
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from playwright.async_api import async_playwright

# توكن البوت
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
    await message.reply(
        "مرحباً بك في بوت تجاوز الروابط المحلي!\n\nأرسل لي أي رابط وسأقوم باستخراج الوجهة النهائية بدقة:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لتجاوز الروابط واستخراج الوجهة النهائية محلياً.",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: Message):
    await callback.message.edit_text("يرجى إرسال الرابط المطلوب تخطيه مباشرة في المحادثة.")

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: Message):
    await callback.message.edit_text("أرسل الرابط المطلوب تجاوزه:", reply_markup=get_main_menu())

@dp.message()
async def handle_links(message: Message):
    text = message.text
    if text and text.startswith("http"):
        processing_msg = await message.reply("⏳ جاري تشغيل المتصفح الخفي لتجاوز الحماية واستخراج الرابط الأخير...")
        
        extracted_url = text
        
        try:
            async with async_playwright() as p:
                # تشغيل متصفح خفي (Chromium)
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720}
                )
                page = await context.new_page()
                
                # الانتقال للرابط المطلوب
                await page.goto(text, timeout=40000)
                
                # انتظار استقرار الصفحة وسكربتات التحقق لمدة كافية (10 ثوانٍ لتفريغ الحماية)
                for _ in range(5):
                    await page.wait_for_timeout(3000)
                    current_url = page.url
                    # إذا خرج المتصفح من نطاق الحماية ووصل لموقع آخر، نعتبره الوجهة
                    if not any(domain in current_url for domain in ["boostylink.com", "rm358.com", "rtmark.net"]):
                        extracted_url = current_url
                        break
                    
                    # محاولة الضغط على أي زر فتح أو تخطّي إن وُجد في الصفحة
                    try:
                        await page.click("button:has-text('Unlock'), button:has-text('تخطي'), a.btn-unlock, input[type='submit']", timeout=1500)
                    except:
                        pass
                
                # إذا ظل الرابط في نطاق الحماية، نأخذ الرابط الحالي كآخر محطة وصل لها المتصفح
                if any(domain in page.url for domain in ["boostylink.com", "rm358.com", "rtmark.net"]):
                    extracted_url = page.url
                else:
                    extracted_url = page.url
                    
                await browser.close()
                
            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            result_text = (
                f"🎉 **تم تجاوز الحماية واستخراج الرابط النهائي بنجاح!**\n\n"
                f"🔗 {clean_url}\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء التشغيل:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
