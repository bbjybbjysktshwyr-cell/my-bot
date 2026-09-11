import os
import re
import cloudscraper
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# توكن البوت الخاص بك
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
        "هذا البوت مخصص لتجاوز الروابط واستخراج الرابط الأصلي.",
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
        processing_msg = await message.reply("⏳ جاري التجاوز... يرجى الانتظار.")
        
        try:
            response = scraper.get(text, timeout=20, allow_redirects=True)
            html_content = response.text
            final_url = response.url
            
            # البحث عن متغيرات التوجيه أو الروابط المقصودة داخل سكربتات الصفحة
            target_match = re.search(r'(?:url|redirect|target|link)["\']?\s*[:=]\s*["\'](https?://[^"\']+)["\']', html_content, re.IGNORECASE)
            
            extracted_url = None
            if target_match:
                extracted_url = target_match.group(1)
            else:
                # نبحث عن أول رابط صالح داخل الصفحة لا يخص الدومين الحالي
                urls_found = re.findall(r'https?://[^\s<>"]+', html_content)
                for u in urls_found:
                    if text not in u and 'boostylink.com' not in u and not u.endswith(('.css', '.js', '.png', '.jpg', '.ico', '.svg', '.json')):
                        extracted_url = u
                        break
            
            # إذا لم نجد رابط خارجي، نعتمد الرابط النهائي للـ Redirect
            if not extracted_url or extracted_url == text:
                extracted_url = final_url

            result_text = (
                f"🎉 **تم تجاوز الرابط بنجاح!**\n\n"
                f"🔗 `{extracted_url}`\n\n"
                f"🔔 اضغط على زر النسخ أدناه للنسخ السريع:"
            )
            
            await processing_msg.edit_text(result_text, reply_markup=get_copy_keyboard(extracted_url))
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء تجاوز الرابط:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
