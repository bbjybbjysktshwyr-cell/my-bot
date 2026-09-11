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
        "مرحباً بك في بوت تجاوز الروابط المحلي!\n\nأرسل لي أي رابط وسأقوم باستخراج الوجهة المخفية:",
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
        processing_msg = await message.reply("⏳ جاري فحص الرابط محلياً...")
        
        extracted_url = text
        
        try:
            # تهيئة كلوود سكريبر مع محاكاة متصفح أندرويد حقيقي
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
                "Referer": text,
                "X-Requested-With": "XMLHttpRequest" # غالباً المواقع تستخدم هذا الهيدر لطلبات الـ AJAX
            }
            
            # جلب الصفحة الأساسية
            response = scraper.get(text, headers=headers, allow_redirects=True, timeout=25)
            html_content = response.text
            
            # محاولة البحث عن أي روابط مخفية داخل كود الـ JSON أو متغيرات الـ Script داخل الصفحة
            # في كثير من الأحيان تكون الروابط مخفية بصيغة JSON ضمن سكربتات الصفحة
            json_match = re.search(r'(\{.*?"url"\s*:\s*"https?://[^"]+".*?\})', html_content)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    if "url" in data:
                        extracted_url = data["url"]
                except:
                    pass
            
            # إذا لم يتم العثور عليها عبر الـ JSON، نبحث عن الروابط النصية الصريحة مع استبعاد الروابط الوهمية
            if extracted_url == text:
                found_links = re.findall(r'https?://[^\s<>"\']+', html_content)
                ignored_domains = [
                    'boostylink.com', 'google.com', 'cloudflare.com', 'w3.org', 
                    'maxcdn', 'jsdelivr', 'jquery', 'bootstrap', 'googletagmanager', 
                    'analytics', '#', 'javascript'
                ]
                
                for link in found_links:
                    clean_l = link.rstrip('\\"\'.,;')
                    if not any(domain in clean_l.lower() for domain in ignored_domains) and clean_l != text:
                        if not clean_l.startswith('#'):
                            extracted_url = clean_l
                            break

            # إذا استمر الرابط كما هو ولم يتغير، نتحقق من الـ Redirect النهائي للسيرفر
            if extracted_url == text and response.url != text and 'boostylink.com' not in response.url:
                extracted_url = response.url

            # تنظيف الرابط النهائي تماماً من أي مسافات أو رموز زائدة
            clean_url = html.unescape(extracted_url).strip()
            clean_url = re.sub(r'\s+', '', clean_url)

            result_text = (
                f"🎉 **تم الاستخراج بنجاح!**\n\n"
                f"🔗 {clean_url}\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ محلي:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
