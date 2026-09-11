import os
import re
import html
import asyncio
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# استيراد آمن لـ Playwright لكي لا يتوقف البوت أبداً إن لم تكن المكتبة مثبتة بالكامل
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

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
        "مرحباً بك! أرسل رابط الاختصار وسأقوم بتجاوز المهام وإحضار الرابط الحقيقي:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لاستخراج الروابط الأصلية وتجاوز المهام بدقة عالية.",
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
        processing_msg = await message.answer("⏳ جاري تحليل الرابط وتصفية المهام واستخراج الهدف النهائي...")
        
        extracted_url = text
        
        # قائمة الحظر الشاملة لكل المهام، السوشيال ميديا، وملفات السي دي إن (CDN)
        excluded_domains = [
            'boostylink.com', 'rm358.com', 'rtmark.net', 
            'youtube.com', 'youtu.be', 't.me', 'telegram.me',
            'discord.gg', 'discord.com', 'instagram.com', 'facebook.com',
            'google.com', 'googletagmanager.com', 'cloudflare.com', 'w3.org',
            'jsdelivr', 'jquery', 'bootstrap', 'html5shiv', 'maxcdn.com', 'oss.maxcdn.com'
        ]
        
        # امتدادات الملفات الممنوعة تماماً (سكربتات، تصميم، صور، ملفات خطوط)
        forbidden_extensions = ('.js', '.css', '.png', '.jpg', '.jpeg', '.ico', '.json', '.xml', '.svg', '.woff', '.ttf')
        
        try:
            # 1. فحص الـ API المباشر (أسرع وأول طريقة)
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

            # 2. محاولة التجاوز المتقدم عبر المتصفح الوهمي (Playwright) إذا لم ينجح الـ API وكان مدعوماً
            if extracted_url == text and PLAYWRIGHT_AVAILABLE:
                try:
                    async with async_playwright() as p:
                        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
                        context = await browser.new_context(
                            user_agent="Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                            viewport={"width": 390, "height": 844}
                        )
                        page = await context.new_page()
                        
                        captured_links = []
                        page.on("response", lambda r: captured_links.append(r.url))
                        
                        await page.goto(text, timeout=30000)
                        await page.wait_for_timeout(3000)
                        
                        # فحص الروابط المستخرجة من الشبكة
                        for link in captured_links:
                            if link and not any(d in link.lower() for d in excluded_domains) and not link.lower().endswith(forbidden_extensions) and link != text and "api" not in link.lower():
                                extracted_url = link
                                break
                        
                        # فحص روابط الصفحة الحالية إذا لم توجد في الشبكة
                        if extracted_url == text:
                            links = await page.evaluate("Array.from(document.querySelectorAll('a')).map(a => a.href)")
                            for link in links:
                                if link and not any(d in link.lower() for d in excluded_domains) and not link.lower().endswith(forbidden_extensions) and link != text:
                                    extracted_url = link
                                    break
                        
                        await browser.close()
                except:
                    pass

            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            if clean_url == text or any(d in clean_url.lower() for d in excluded_domains) or clean_url.lower().endswith(forbidden_extensions):
                await processing_msg.edit_text("⚠️ الرابط محمي بمهام تفاعلية مكثفة تتطلب فتح الصفحة يدوياً.")
            else:
                result_text = (
                    f"🎉 **تم استخراج الرابط الحقيقي بنجاح!**\n\n"
                    f"🔗 {clean_url}\n\n"
                    f"🔔 اضغط على زر النسخ أدناه:"
                )
                await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
                
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ:\n`{str(e)}`")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 البوت يعمل الآن بكفاءة ويستمع للأوامر...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
