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
        "مرحباً بك! أرسل رابط الاختصار (مثل Boostylink أو Link-center) وسأقوم باستخراج الرابط الحقيقي:",
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
        processing_msg = await message.answer("⏳ جاري فحص الرابط وتتبع مسار التوجيه واستخراج الهدف...")
        
        extracted_url = text
        
        excluded_domains = [
            'boostylink.com', 'link-center.net', 'rm358.com', 'rtmark.net', 
            'youtube.com', 'youtu.be', 't.me', 'telegram.me',
            'discord.gg', 'discord.com', 'instagram.com', 'facebook.com',
            'google.com', 'googletagmanager.com', 'cloudflare.com', 'w3.org',
            'jsdelivr', 'jquery', 'bootstrap', 'html5shiv', 'maxcdn.com', 'oss.maxcdn.com'
        ]
        forbidden_extensions = ('.js', '.css', '.png', '.jpg', '.jpeg', '.ico', '.json', '.xml', '.svg', '.woff', '.ttf')
        
        try:
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'android', 'desktop': False}
            )
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                "Referer": text
            }
            
            # محاولة فحص الـ API الخاص بـ Boostylink أو Link-center إن وجد
            path_parts = text.rstrip('/').split('/')
            slug = path_parts[-1] if path_parts else ""
            if slug and len(slug) > 2:
                for api_endpoint in [f"https://boostylink.com/api/links/{slug}", f"https://link-center.net/api/links/{slug}"]:
                    try:
                        api_resp = scraper.get(api_endpoint, headers=headers, timeout=5)
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

            # تتبع مسار التحويلات والروابط المخفية عبر الـ HTTP والصفحة
            if extracted_url == text:
                response = scraper.get(text, headers=headers, allow_redirects=True, timeout=15)
                html_content = response.text
                
                if response.history:
                    for resp in response.history:
                        loc = resp.headers.get("Location")
                        if loc and not any(d in loc.lower() for d in excluded_domains):
                            extracted_url = loc
                            break

                if extracted_url == text:
                    js_redirects = re.findall(r'(?:window\.location|location\.href|href|destination)\s*[:=]\s*["\'](https?://[^"\']+)["\']', html_content, re.IGNORECASE)
                    for match in js_redirects:
                        if not any(d in match.lower() for d in excluded_domains) and not match.lower().endswith(forbidden_extensions):
                            extracted_url = match
                            break

                if extracted_url == text:
                    found_links = re.findall(r'https?://[^\s<>"\']+', html_content)
                    for link in found_links:
                        clean_l = link.rstrip('\\"\'.,;')
                        if clean_l != text and not any(d in clean_l.lower() for d in excluded_domains) and not clean_l.lower().endswith(forbidden_extensions):
                            extracted_url = clean_l
                            break

            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            if clean_url == text or any(d in clean_url.lower() for d in excluded_domains) or clean_url.lower().endswith(forbidden_extensions):
                await processing_msg.edit_text(
                    "⚠️ **هذا الرابط يتطلب تخطي حماية تفاعلية**\n\n"
                    "يمكنك فتحه مباشرة عبر الرابط أدناه:",
                    reply_markup=get_copy_keyboard(text)
                )
            else:
                result_text = (
                    f"🎉 **تم استخراج الرابط الحقيقي بنجاح!**\n\n"
                    f"🔗 {clean_url}\n\n"
                    f"🔔 اضغط على زر النسخ أدناه:"
                )
                await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
                
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء المعالجة:\n`{str(e)}`")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 البوت يعمل الآن بكفاءة...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
