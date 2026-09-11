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
        "هذا البوت مخصص لتجاوز الروابط واستخراج الرابط الأصلي بدقة.",
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
            
            extracted_url = None
            
            # 1. البحث أولاً عن روابط فيديوهات يوتيوب الفعلية (مثل youtu.be أو youtube.com/watch)
            yt_match = re.search(r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s<>"\']+)', html_content)
            if yt_match:
                extracted_url = yt_match.group(1)
            else:
                # 2. البحث عن متغيرات التوجيه المعتادة
                target_match = re.search(r'(?:url|redirect|target|link|destination)["\']?\s*[:=]\s*["\'](https?://[^"\']+)["\']', html_content, re.IGNORECASE)
                if target_match:
                    extracted_url = target_match.group(1)
                else:
                    # 3. البحث العام مع استبعاد القنوات وروابط السوشيال ميديا العامة
                    urls_found = re.findall(r'https?://[^\s<>"]+', html_content)
                    ignored = ['boostylink.com', 'googletagmanager.com', 'discord.gg', '@', 'facebook', 'twitter', 'instagram']
                    for u in urls_found:
                        if text not in u and not any(i in u for i in ignored) and not u.endswith(('.css', '.js', '.png', '.jpg', '.ico', '.svg')):
                            extracted_url = u
                            break
            
            # إذا لم نجد شيئاً، نعتمد الرابط النهائي
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
