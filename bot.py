import os
import re
import html
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from playwright.async_api import async_playwright

TOKEN = "8512256766:AAGmFS1y0JnmACIb42bDGREbZ-gcfPliev4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_copy_keyboard(target_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 نسخ الرابط", url=target_url)]
    ])

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.reply("أهلاً بك. أرسل رابط البوستر أو الاختصار وسأقوم بتجاوزه وإرسال الرابط النهائي مباشرة:")

@dp.message()
async def handle_links(message: Message):
    text = message.text
    if text and text.startswith("http"):
        processing_msg = await message.reply("⏳ جاري فتح المتصفح وتجاوز المهام والأزرار تلقائياً...")
        
        extracted_url = text
        
        try:
            async with async_playwright() as p:
                # تشغيل المتصفح
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(text, timeout=60000)
                await page.wait_for_timeout(3000)
                
                # محاولة الضغط على الأزرار المتعددة للمهام لتفعيل شريط التقدم
                for _ in range(5):
                    try:
                        buttons = await page.query_selector_all("a.btn, button, .red, .blue")
                        for btn in buttons:
                            await btn.click(timeout=1000)
                            await page.wait_for_timeout(1000)
                    except:
                        pass
                
                # الانتظار والنقر على زر فتح القفل الأخضر (Unlock link)
                try:
                    await page.wait_for_selector("text=Unlock link", timeout=10000)
                    await page.click("text=Unlock link", timeout=3000)
                    await page.wait_for_timeout(5000) # انتظار التحويل للرابط النهائي
                except:
                    pass
                
                extracted_url = page.url
                await browser.close()
                
            clean_url = html.unescape(extracted_url).strip()
            
            if "boostylink.com" in clean_url or "rm358.com" in clean_url:
                await processing_msg.edit_text("⚠️ لم يكتمل التخطي التلقائي لأن الموقع يتطلب تفاعلاً بشرياً عميقاً.")
            else:
                await processing_msg.edit_text(
                    f"🎉 **تم استخراج الرابط النهائي:**\n\n{clean_url}",
                    reply_markup=get_copy_keyboard(clean_url)
                )
                
        except Exception as e:
            await processing_msg.edit_text(f"❌ تأكد من تثبيت متصفح Playwright على السيرفر الخاص بك.\nالخطأ: {str(e)}")
    else:
        await message.reply("يرجى إرسال رابط صحيح.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
