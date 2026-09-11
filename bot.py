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
        [InlineKeyboardButton(text="🔗 فحتجاوز رابط", callback_data="bypass_link")],
        [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")]
    ])
    return keyboard

@dp.message(Command("start"))
async def send_welcome(message: Message):
    welcome_text = (
        "مرحباً بك في بوت تجاوز الروابط الذكي!\n\n"
        "أرسل لي أي رابط (مثل Boosty) وسأقوم بفحصه واستخراج الرابط المخفي:"
    )
    await message.reply(welcome_text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "about")
async def about_callback(callback: Message):
    await callback.message.edit_text(
        "هذا البوت مخصص لتجاوز الروابط وحماية Cloudflare واستخراج الروابط الداخلية.",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: Message):
    await callback.message.edit_text(
        "يرجى إرسال الرابط المطلوب تخطيه مباشرة في المحادثة."
    )

@dp.message()
async def handle_links(message: Message):
    text = message.text
    if text and text.startswith("http"):
        processing_msg = await message.reply("جارٍ فحص الصفحة والبحث عن الرابط المخفي...")
        
        try:
            response = scraper.get(text, timeout=20)
            html_content = response.text
            
            # البحث عن روابط خارجية أو روابط توجيه داخل HTML باستخدام Regular Expressions
            urls_found = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', html_content)
            
            # تصفية الروابط واستبعاد روابط الموقع نفسه أو الملفات البرمجية
            filtered_urls = [u for u in set(urls_found) if text not in u and 'boostylink.com' not in u and not u.endswith(('.css', '.js', '.png', '.jpg', '.ico'))]
            
            if filtered_urls:
                links_text = "\n".join(filtered_urls[:5]) # عرض أول 5 روابط يتم العثور عليها
                result_text = (
                    f"✅ **تم استخراج الروابط من الصفحة بنجاح!**\n\n"
                    f"🔗 **الروابط المكتشفة:**\n{links_text}"
                )
            else:
                result_text = (
                    f"🔗 **الرابط النهائي:**\n{response.url}\n\n"
                    f"⚠️ لم يتم العثور على روابط توجيه مخفية داخل الصفحة، قد يتطلب تفاعلاً يدوياً."
                )
                
            await processing_msg.edit_text(result_text)
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء فحص الرابط:\n`{str(e)}`")
    else:
        await message.reply("يرجى إرسال رابط صالح يبدأ بـ http أو https.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
