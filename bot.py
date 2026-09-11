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

# إنشاء سكربت تجاوز الكلاود فلير
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
        processing_msg = await message.reply("⏳ جاري تجاوز الرابط وتصفية الإعلانات...")
        
        try:
            response = scraper.get(text, timeout=25, allow_redirects=True)
            html_content = response.text
            final_url = response.url
            
            extracted_url = None
            
            # البحث عن أوامر التوجيه داخل السكربتات
            location_match = re.search(r'window\.location(?:\.href|\.replace)?\s*=\s*["\'](https?://[^"\']+)["\']', html_content, re.IGNORECASE)
            if location_match:
                extracted_url = location_match.group(1)
            
            if not extracted_url:
                target_match = re.search(r'["\'](?:target|destination|finalUrl|redirect_url|link|url|to)["\']\s*[:=]\s*["\'](https?://[^"\']+)["\']', html_content, re.IGNORECASE)
                if target_match:
                    extracted_url = target_match.group(1)
            
            if not extracted_url:
                all_urls = re.findall(r'https?://[^\s<>"\']+', html_content)
                # أضفنا rm358.com وباقي شبكات الإعلانات إلى قائمة التجاهل
                ignored = [
                    'boostylink.com', 'rm358.com', 'googletagmanager.com', 
                    'google-analytics.com', 'discord.gg', 'youtube.com', 
                    'youtu.be', 'facebook', 'twitter', 'instagram', 'adsterra'
                ]
                
                filtered = []
                for u in all_urls:
                    if text not in u and not any(ig in u for ig in ignored) and not u.endswith(('.css', '.js', '.png', '.jpg', '.ico', '.svg', '.json')):
                        filtered.append(u)
                
                if filtered:
                    extracted_url = filtered[-1]
            
            if not extracted_url or extracted_url == text:
                extracted_url = final_url

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
