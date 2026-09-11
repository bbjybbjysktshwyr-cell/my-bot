import os
import re
import html
import json
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

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
        "مرحباً بك من جديد! البوت يعمل الآن بشكل مستقر.\n\nأرسل لي الرابط وسأقوم بفحصه واستخراج وجهته:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لفحص واستخراج الروابط بكفاءة عالية.",
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
        processing_msg = await message.reply("⏳ جاري فحص الرابط واستخراج النتائج...")
        
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
            
            # فحص الـ API الخاص بـ boostylink مباشرة لو وجد السلاج
            path_parts = text.rstrip('/').split('/')
            slug = path_parts[-1] if path_parts else ""
            if slug and len(slug) > 2:
                try:
                    api_resp = scraper.get(f"https://boostylink.com/api/links/{slug}", headers=headers, timeout=8)
                    if api_resp.status_code == 200:
                        api_data = api_resp.json()
                        for key in ["destination", "target_url", "url", "link"]:
                            if key in api_data and api_data[key]:
                                extracted_url = api_data[key]
                                break
                except:
                    pass

            # فحص الروابط داخل محتوى الصفحة إذا لم يتم جلب الوجهة
            if extracted_url == text:
                found_links = re.findall(r'https?://[^\s<>"\']+', html_content)
                ignored = ['boostylink.com', 'google.com', 'cloudflare.com', 'w3.org', 'rm358.com', 'rtmark.net']
                for link in found_links:
                    clean_l = link.rstrip('\\"\'.,;')
                    if not any(d in clean_l.lower() for d in ignored) and clean_l != text:
                        extracted_url = clean_l
                        break

            if extracted_url == text and response.url != text:
                extracted_url = response.url

            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            result_text = (
                f"🎉 **النتيجة النهائية:**\n\n"
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
