import os
import re
import html
import asyncio
import cloudscraper
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
        "مرحباً بك! أرسل رابط الاختصار وسأقوم بتجاوز المهام وإحضار الرابط الحقيقي:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لاستخراج الروابط الأصلية وتجاوز المهام بدقة عالية.",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: Message):
    await callback.message.edit_text("يرجى إرسال الرابط مباشرة في المحادثة.")

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: Message):
    await callback.message.edit_text("أرسل الرابط المطلوب فحصه:", reply_markup=get_main_menu())

@dp.message()
async def handle_links(message: Message):
    text = message.text
    if text and text.startswith("http"):
        processing_msg = await message.reply("⏳ جاري مراقبة الشبكة وتجاوز المهام واكتشاف الرابط...")
        
        extracted_url = text
        
        # قائمة الحظر الشاملة للمهام والملفات
        excluded_domains = [
            'boostylink.com', 'rm358.com', 'rtmark.net', 
            'youtube.com', 'youtu.be', 't.me', 'telegram.me',
            'discord.gg', 'discord.com', 'instagram.com', 'facebook.com',
            'google.com', 'googletagmanager.com', 'cloudflare.com', 'w3.org',
            'jsdelivr', 'jquery', 'bootstrap', 'html5shiv', 'maxcdn.com', 'oss.maxcdn.com'
        ]
        forbidden_extensions = ('.js', '.css', '.png', '.jpg', '.jpeg', '.ico', '.json', '.xml', '.svg', '.woff', '.ttf')
        
        try:
            # 1. محاولة الفحص السريع عبر الـ API المباشر
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'android', 'desktop': False}
            )
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                "Referer": text
            }
            
            path_parts = text.rstrip('/').split('/')
            slug = path_parts[-1] if path_parts else ""
            if slug and len(slug) > 2:
                try:
                    api_resp = scraper.get(f"https://boostylink.com/api/links/{slug}", headers=headers, timeout=6)
                    if api_resp.status_code == 200:
                        api_data = api_resp.json()
                        for key in ["destination", "target_url", "url", "link", "target", "final_url"]:
                            if key in api_data and api_data[key]:
                                val = str(api_data[key])
                                if not any(d in val.lower() for d in excluded_domains) and not val.lower().endswith(forbidden_extensions):
                                    extracted_url = val
                                    break
                except:
                    pass

            # 2. التجاوز المتقدم عبر Playwright مع اعتراض الطلبات (Network Interception)
            if extracted_url == text:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        headless=True,
                        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                    )
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                        viewport={"width": 390, "height": 844}
                    )
                    page = await context.new_page()
                    
                    # التقاط الرابط الحقيقي من استجابات الشبكة الداخلية والخلفية للموقع
                    captured_links = []
                    page.on("response", lambda response: captured_links.append(response.url))
                    
                    await page.goto(text, timeout=50000)
                    await page.wait_for_timeout(4000)
                    
                    # محاولة النقر المتكرر على الأزرار الوهمية لمحاكاة المستخدم
                    for _ in range(4):
                        try:
                            for selector in ["a.btn", "button", ".red", ".blue", "#btn", ".unlock-btn", "text=Continue", "text=Unlock", "text=Verify"]:
                                element = await page.query_selector(selector)
                                if element:
                                    await element.click(timeout=2000)
                                    await page.wait_for_timeout(2500)
                        except:
                            pass
                    
                    await page.wait_for_timeout(3000)
                    
                    # فحص الروابط الملتقطة من الشبكة أولاً (أكثر دقة)
                    for link in captured_links:
                        if link and not any(d in link.lower() for d in excluded_domains) and not link.lower().endswith(forbidden_extensions) and link != text and "api" not in link.lower():
                            extracted_url = link
                            break
                    
                    # إذا لم يوجد في الشبكة، نفحص روابط الصفحة الحالية
                    if extracted_url == text:
                        links = await page.evaluate("Array.from(document.querySelectorAll('a')).map(a => a.href)")
                        for link in links:
                            if link and not any(d in link.lower() for d in excluded_domains) and not link.lower().endswith(forbidden_extensions) and link != text:
                                extracted_url = link
                                break
                    
                    if extracted_url == text and page.url != text:
                        if not any(d in page.url.lower() for d in excluded_domains):
                            extracted_url = page.url

                    await browser.close()

            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            if clean_url == text or any(d in clean_url.lower() for d in excluded_domains) or clean_url.lower().endswith(forbidden_extensions):
                await processing_msg.edit_text("⚠️ الموقع يتطلب تحقق بشري (Captcha) ولا يمكن تجاوزه تلقائياً بالكامل.")
            else:
                result_text = (
                    f"🎉 **تم استخراج الرابط الحقيقي بنجاح!**\n\n"
                    f"🔗 {clean_url}\n\n"
                    f"🔔 اضغط على زر النسخ أدناه:"
                )
                await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
                
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
