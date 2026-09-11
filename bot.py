import os
import re
import html
import json
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
    await message.reply(
        "مرحباً بك! أرسل رابط الاختصار وسأقوم بتصفية الروابط وإحضار الهدف النهائي:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لاستخراج الروابط الأصلية بدقة وتجاوز المهام.",
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
        processing_msg = await message.reply("⏳ جاري تحليل الرابط وتصفية النتائج...")
        
        extracted_url = text
        
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'android',
                    'desktop': False
                }
            )
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
                "Referer": text
            }
            
            response = scraper.get(text, headers=headers, allow_redirects=True, timeout=20)
            html_content = response.text
            
            # --- [التحديث المضاف فوق الأساسيات: قائمة حظر شاملة لكل المهام والملفات والوسائط] ---
            excluded_domains = [
                'boostylink.com', 'rm358.com', 'rtmark.net', 
                'youtube.com', 'youtu.be', 't.me', 'telegram.me',
                'discord.gg', 'discord.com', 'instagram.com', 'facebook.com',
                'google.com', 'googletagmanager.com', 'cloudflare.com', 'w3.org',
                'jsdelivr', 'jquery', 'bootstrap', 'html5shiv', 'maxcdn.com', 'oss.maxcdn.com'
            ]
            forbidden_extensions = ('.js', '.css', '.png', '.jpg', '.jpeg', '.ico', '.json', '.xml', '.svg', '.woff', '.ttf')
            
            # 1. فحص الـ API الرسمي للمنصة
            path_parts = text.rstrip('/').split('/')
            slug = path_parts[-1] if path_parts else ""
            if slug and len(slug) > 2:
                try:
                    api_resp = scraper.get(f"https://boostylink.com/api/links/{slug}", headers=headers, timeout=8)
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

            # 2. البحث داخل متغيرات السكربتات البرمجية المخفية
            if extracted_url == text:
                js_var_matches = re.findall(r'(?:destination|target|url|link|goUrl|hopUrl|redirect)\s*[:=]\s*["\'](https?://[^"\']+)["\']', html_content, re.IGNORECASE)
                for match in js_var_matches:
                    if not any(d in match.lower() for d in excluded_domains) and not match.lower().endswith(forbidden_extensions):
                        extracted_url = match
                        break

            # 3. الفحص العام وتصفية أي رابط لا يطابق شروط الحظر
            if extracted_url == text:
                found_links = re.findall(r'https?://[^\s<>"\']+', html_content)
                for link in found_links:
                    clean_l = link.rstrip('\\"\'.,;')
                    if clean_l != text and not any(d in clean_l.lower() for d in excluded_domains) and not clean_l.lower().endswith(forbidden_extensions):
                        extracted_url = clean_l
                        break

            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            # --- [التحقق النهائي من النتائج] ---
            if clean_url == text or any(d in clean_url.lower() for d in excluded_domains) or clean_url.lower().endswith(forbidden_extensions):
                await processing_msg.edit_text("⚠️ الرابط محمي بمهام تفاعلية ولا يمكن استخلاص وجهته النهائية إلا بالفتح اليدوي.")
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
    import asyncio
    asyncio.run(dp.start_polling(bot))
