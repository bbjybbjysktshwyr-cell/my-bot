import os
import re
import html
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

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
        processing_msg = await message.reply("⏳ جاري تفحص مسار التوجيه وسحب الرابط...")
        
        extracted_url = None
        
        try:
            # تتبع تاريخ الطلبات وسلسلة التحويلات (Redirect History) بدقة
            session = cloudscraper.create_scraper()
            response = session.get(text, timeout=30, allow_redirects=True)
            
            # فحص سجل الـ Redirects بالكامل إذا وجد
            if response.history:
                for resp in response.history:
                    if 'link-center.net' in resp.url or ('boostylink.com' not in resp.url and 'rm358.com' not in resp.url):
                        extracted_url = resp.url
                        break
            
            # إذا لم نجد في التاريخ، نفحص الـ URL النهائي للاستجابة
            if not extracted_url and response.url and response.url != text:
                if 'link-center.net' in response.url or 'boostylink.com' not in response.url:
                    extracted_url = response.url

            # فحص محتوى الصفحة الـ HTML في حال كان الرابط مخفياً بداخل نصوص السكربتات المتقدمة
            if not extracted_url or extracted_url == text:
                html_content = response.text
                match_lc = re.search(r'https?://link-center\.net/[^\s<>"\']+', html_content, re.IGNORECASE)
                if match_lc:
                    extracted_url = match_lc.group(0)
                else:
                    # البحث عن أي رابط أجنبي غير إعلاني
                    all_urls = re.findall(r'https?://[^\s<>"\']+', html_content)
                    for u in all_urls:
                        u_clean = u.rstrip('\\"\'.,;')
                        if 'boostylink.com' not in u_clean and 'rm358.com' not in u_clean and 'googletagmanager' not in u_clean:
                            if u_clean != text:
                                extracted_url = u_clean
                                break

            if not extracted_url:
                extracted_url = text

            clean_url = html.unescape(extracted_url)

            result_text = (
                f"🎉 **تم استخراج الرابط بنجاح!**\n\n"
                f"🔗 `{clean_url}`\n\n"
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
