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
        "مرحباً بك في بوت تجاوز الروابط الذكي!\n\nأرسل لي رابط Boostylink وسأقوم بتخطي المهام واستخراج الرابط النهائي:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لتجاوز روابط المهام وإلغاء القفل تلقائياً.",
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
        processing_msg = await message.reply("⏳ جاري محاكاة المهام وتخطي قفل الأزرار...")
        
        extracted_url = text
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720}
                )
                page = await context.new_page()
                
                # التقاط طلبات الشبكة (Network Requests) لأن السيرفر أحياناً يكشف الرابط عبر الـ API عند الفتح
                captured_urls = []
                page.on("request", lambda req: captured_urls.append(req.url))
                
                await page.goto(text, timeout=45000)
                await page.wait_for_load_timeout(4000)
                
                # محاولة الضغط البرمجي على الأزرار الوهمية أو محاكاة فتحها لتفعيل شريط التقدم
                for _ in range(3):
                    try:
                        # البحث عن أزرار الاشتراك أو المشاهدة والنقر عليها لفتحها وإغلاقها تلقائياً
                        buttons = await page.query_selector_all("a.btn, button, .red, [id*='btn']")
                        for btn in buttons:
                            try:
                                await btn.click(timeout=1000)
                                await page.wait_for_timeout(1000)
                            except:
                                pass
                    except:
                        pass
                
                # الانتظار حتى يصبح الزر الأخضر (Unlock link) متاحاً والنقر عليه
                try:
                    await page.wait_for_selector("text=Unlock link", timeout=10000)
                    # النقر على الزر الأخضر لإظهار الرابط النهائي
                    await page.click("text=Unlock link", timeout=3000)
                    await page.wait_for_timeout(4000)
                except:
                    pass
                
                # فحص الروابط المسجلة في الشبكة أو الرابط الحالي للمتصفح
                current_url = page.url
                if not any(d in current_url for d in ["boostylink.com", "rm358.com", "rtmark.net"]):
                    extracted_url = current_url
                else:
                    # البحث في الطلبات المسجلة عن رابط حقيقي خارج المنصة
                    found_target = False
                    for u in reversed(captured_urls):
                        if not any(d in u for d in ["boostylink.com", "rm358.com", "rtmark.net", "google", "cloudflare", "static"]):
                            if u.startswith("http"):
                                extracted_url = u
                                found_target = True
                                break
                    if not found_target:
                        extracted_url = page.url
                
                await browser.close()
                
            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            result_text = (
                f"🎉 **تم تجاوز المهام واستخراج الرابط النهائي!**\n\n"
                f"🔗 {clean_url}\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء التجاوز:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
