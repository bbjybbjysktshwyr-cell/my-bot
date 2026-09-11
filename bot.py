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
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 فحص وتجاوز رابط", callback_data="bypass_link")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ])
    return keyboard

def get_copy_keyboard(target_url):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 نسخ الرابط", url=target_url)],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])
    return keyboard

@dp.message(Command("start"))
async def send_welcome(message: Message):
    welcome_text = (
        "مرحباً بك في بوت تجاوز الروابط الذكي!\n\n"
        "أرسل لي أي رابط وسأقوم باستخراج الرابط الأصلي بدقة:"
    )
    await message.reply(welcome_text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لتجاوز روابط الحماية واستخراج الرابط النهائي.",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: Message):
    await callback.message.edit_text(
        "يرجى إرسال الرابط المطلوب تخطيه مباشرة في المحادثة."
    )

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: Message):
    await callback.message.edit_text(
        "مرحباً بك مرة أخرى! أرسل الرابط المطلوب تجاوزه:",
        reply_markup=get_main_menu()
    )

@dp.message()
async def handle_links(message: Message):
    text = message.text
    if text and text.startswith("http"):
        processing_msg = await message.reply("⏳ جاري تجاوز الرابط واستخراج الوجهة المخفية...")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Referer": text,
                "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
            }
            
            response = scraper.get(text, headers=headers, timeout=25, allow_redirects=True)
            html_content = response.text
            
            extracted_url = None
            
            # 1. البحث عن رابط link-center بشكل مباشر داخل النصوص أو الكود المصدري
            link_center_match = re.search(r'https?://link-center\.net/[^\s<>"\']+', html_content, re.IGNORECASE)
            if link_center_match:
                extracted_url = link_center_match.group(0)
            
            # 2. البحث داخل روابط الـ Form action أو أزرار التوجيه
            if not extracted_url:
                form_match = re.search(r'<form[^>]+action=["\'](https?://[^"\']+)["\']', html_content, re.IGNORECASE)
                if form_match:
                    candidate = form_match.group(1)
                    if 'boostylink.com' not in candidate:
                        extracted_url = candidate

            # 3. البحث عن أي روابط مخفية داخل وسوم الـ a أو السكربتات
            if not extracted_url:
                all_urls = re.findall(r'https?://[^\s<>"\']+', html_content)
                ignored = [
                    'boostylink.com', 'rm358.com', 'googletagmanager.com', 
                    'google-analytics.com', 'discord.gg', 'youtube.com', 
                    'youtu.be', 'facebook', 'twitter', 'instagram', 'adsterra',
                    'cloudflare.com', 'w3.org', 'schema.org', 'jquery', 'bootstrap'
                ]
                
                for u in all_urls:
                    # تنظيف الرابط من الرموز الزائدة بالنهاية
                    u_clean = u.rstrip('\\"\'.,;')
                    if not any(ig in u_clean for ig in ignored) and not u_clean.endswith(('.css', '.js', '.png', '.jpg', '.ico', '.svg', '.json')):
                        if u_clean != text:
                            extracted_url = u_clean
                            break
            
            # إذا استمر الفشل، نستخدم الرابط النهائي للطلب
            if not extracted_url or extracted_url == text:
                extracted_url = response.url

            clean_url = html.unescape(extracted_url)

            result_text = (
                f"🎉 **تم تجاوز الرابط بنجاح!**\n\n"
                f"🔗 `{clean_url}`\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(clean_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء تجاوز الرابط:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
