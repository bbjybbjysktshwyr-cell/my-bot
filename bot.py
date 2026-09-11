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
scraper = cloudscraper.create_scraper()

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
        processing_msg = await message.reply("⏳ جاري فحص الرابط واستخراج الوجهة المخفية...")
        
        extracted_url = None
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Referer": text
            }
            
            response = scraper.get(text, headers=headers, allow_redirects=True, timeout=25)
            html_content = response.text
            
            # 1. البحث المباشر عن روابط التوجيه المعروفة
            match = re.search(r'https?://(?:link-center|linkvertise)\.net/[^\s<>"\']+', html_content, re.IGNORECASE)
            if match:
                extracted_url = match.group(0)
            else:
                # 2. فحص شامل مع فلترة صارمة جداً لاستبعاد ملفات الـ CDN والسكربتات والإعلانات
                found_links = re.findall(r'https?://[^\s<>"\']+', html_content)
                ignored_keywords = [
                    'boostylink.com', 'google.com', 'cloudflare.com', 'w3.org', 
                    'maxcdn', 'jsdelivr', 'cloudflare', 'jquery', 'bootstrap', 
                    'googletagmanager', 'analytics', '.js', '.css', '.png', '.jpg', '.ico'
                ]
                
                for link in found_links:
                    clean_l = link.rstrip('\\"\'.,;')
                    # التأكد من أن الرابط لا يحتوي على أي كلمة من القائمة السوداء ولا ينتهي بملف برمجي
                    if not any(word in clean_l.lower() for word in ignored_keywords) and clean_l != text:
                        if 'link-center' in clean_l or 'linkvertise' in clean_l or 'download' in clean_l or 'to/' in clean_l:
                            extracted_url = clean_l
                            break
            
            # إذا لم يتم العثور على رابط صالح، نتحقق من الـ Redirect النهائي للسيرفر
            if not extracted_url or extracted_url == text:
                if response.url != text and 'boostylink.com' not in response.url:
                    extracted_url = response.url
                else:
                    extracted_url = text

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
