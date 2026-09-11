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
        processing_msg = await message.reply("⏳ جاري فتح المتصفح وتجاوز صفحات التحقق والأزرار...")
        
        extracted_url = text
        
        try:
            async with async_playwright() as p:
                # تشغيل متصفح خفي
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
                )
                page = await context.new_page()
                
                # فتح الرابط الأول
                await page.goto(text, timeout=30000)
                await page.wait_for_load_timeout(5000) # انتظار تحميل التحقق
                
                # فحص إذا كان الرابط يمر عبر boostylink جلب الوجهة منها
                if "boostylink.com" in page.url:
                    try:
                        # محاولة الضغط على زر المتابعة أو تخطي التحقق إن وجد
                        await page.click("button, a.btn, input[type='submit']", timeout=3000)
                        await page.wait_for_load_timeout(4000)
                    except:
                        pass
                
                # تتبع التحويلات وتجاوز صفحات rm358 أو rtmark بانتظار استقرار الرابط النهائي
                for _ in range(3):
                    current_url = page.url
                    if any(domain in current_url for domain in ["rm358.com", "rtmark.net", "boostylink.com"]):
                        try:
                            # انتظار أي تفاعل أو تحويل تلقائي بعد التحقق
                            await page.wait_for_load_state("networkidle", timeout=8000)
                        except:
                            # محاولة النقر على أي زر محتمل للتحقق لو توقفت الصفحة عنده
                            try:
                                await page.click("button, input[type='submit'], a", timeout=2000)
                                await page.wait_for_timeout(3000)
                            except:
                                break
                    else:
                        break
                
                extracted_url = page.url
                await browser.close()
                
            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            result_text = (
                f"🎉 **تم تجاوز التحقق واستخراج الرابط النهائي بنجاح!**\n\n"
                f"🔗 {clean_url}\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء التخطي:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
