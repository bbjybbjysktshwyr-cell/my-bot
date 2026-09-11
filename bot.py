import os
import re
import html
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
        "مرحباً بك في بوت تجاوز الروابط الذكي!\n\nأرسل لي أي رابط وسأقوم باستخراج الرابط الأصلي بدقة:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لتجاوز روابط الحماية واستخراج الرابط النهائي.",
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
        processing_msg = await message.reply("⏳ جاري سحب الرابط النهائي الحقيقي...")
        
        extracted_url = text
        
        try:
            # استخدام جلسة cloudscraper متقدمة مع محاكاة كاملة للمتصفح
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'android',
                    'desktop': False
                }
            )
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
                "Referer": text
            }
            
            # الطلب الأول لصفحة البوستي
            response = scraper.get(text, headers=headers, allow_redirects=True, timeout=25)
            html_content = response.text
            
            # البحث عن أي روابط توجيه نهائية مخفية ضمن الأكواد أو الـ JavaScript أو الأطر
            # 1. البحث عن روابط link-center أو bstshrt أو أي روابط وجهة صريحة
            found_links = re.findall(r'https?://[^\s<>"\']+', html_content)
            ignored_domains = ['boostylink.com', 'google.com', 'cloudflare.com', 'w3.org', 'maxcdn', 'jsdelivr', 'jquery', 'bootstrap', 'googletagmanager', 'analytics']
            
            target_candidate = None
            for link in found_links:
                clean_l = link.rstrip('\\"\'.,;')
                if not any(domain in clean_l.lower() for domain in ignored_domains) and clean_l != text:
                    if any(domain in clean_l.lower() for domain in ['link-center', 'bstshrt', 'linkvertise', 'ouo.io', 'adf.ly', 'go.', 'to/']):
                        target_candidate = clean_l
                        break
            
            if target_candidate:
                extracted_url = target_candidate
            elif response.url != text and 'boostylink.com' not in response.url:
                extracted_url = response.url
            else:
                # إذا كانت الصفحة محمية بالكامل بسكربت خارجي، نبحث عن روابط إعادة التوجيه بداخل الـ Meta tags أو الـ window.location
                meta_match = re.search(r'(?:window\.location\.href|url|href)\s*=\s*["\'](https?://[^"\']+)["\']', html_content, re.IGNORECASE)
                if meta_match:
                    extracted_url = meta_match.group(1)

            # تنظيف الرابط النهائي وجعله بسطر واحد نظيف تماماً
            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            result_text = (
                f"🎉 **تم استخراج الرابط بنجاح!**\n\n"
                f"🔗 {clean_url}\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
