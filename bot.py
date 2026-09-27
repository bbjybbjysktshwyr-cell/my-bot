import os
import json
import asyncio
import subprocess
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "8618789887:AAGKxnDN6a0ulOS9aLyB1HnuNygukFsIVHs"
API_URL = "http://127.0.0.1:2233/delta"

bot = Bot(token=TOKEN)
dp = Dispatcher()

RATINGS_FILE = "ratings.json"

# قائمة القنوات الإجبارية مع روابطها
REQUIRED_CHANNELS = [
    {"name": "DiamondAccStore", "url": "https://t.me/DiamondAccStore", "id": "@DiamondAccStore"},
    {"name": "DiamondStore_1", "url": "https://t.me/DiamondStore_1", "id": "@DiamondStore_1"},
    {"name": "DI_Script", "url": "https://t.me/DI_Script", "id": "@DI_Script"}
]

def load_ratings():
    if os.path.exists(RATINGS_FILE):
        try:
            with open(RATINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [{"name": "M", "stars": "⭐⭐⭐⭐⭐", "text": "ممتاز جداً وسريع"}]

def save_ratings():
    try:
        with open(RATINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(bot_ratings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في حفظ التقييمات: {e}")

user_languages = {}
bot_ratings = load_ratings()
completed_orders = 7

class RatingStates(StatesGroup):
    waiting_for_review_text = State()

server_process = None

def start_local_server():
    global server_process
    if server_process is None:
        server_process = subprocess.Popen(["python", "server.py", "--port", "2233"])
        print("🚀 تم تشغيل سيرفر دلتا المحلي تلقائياً في الخلفية...")

# دالة لفحص القنوات غير المشترك فيها فقط
async def get_unsubscribed_channels(user_id: int):
    unsubscribed = []
    for ch in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                unsubscribed.append(ch)
        except Exception:
            unsubscribed.append(ch)
    return unsubscribed

def get_main_menu(lang="ar"):
    global completed_orders
    if lang == "en":
        keyboard = [
            [InlineKeyboardButton(text="⚡️ Bypass Delta Link", callback_data="bypass_link")],
            [InlineKeyboardButton(text="⭐ Bot Ratings 🟢", callback_data="ratings_page_0")],
            [InlineKeyboardButton(text="🌐 Change Language", callback_data="change_lang")],
            [InlineKeyboardButton(text="ℹ️ About Bot", callback_data="about")],
            [InlineKeyboardButton(text=f"✅ Completed Orders: {completed_orders}", callback_data="orders_info")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    else:
        keyboard = [
            [InlineKeyboardButton(text="⚡️ تجاوز رابط دلتا", callback_data="bypass_link")],
            [InlineKeyboardButton(text="⭐ تقييمات البوت 🟢", callback_data="ratings_page_0")],
            [InlineKeyboardButton(text="🌐 تغيير اللغة", callback_data="change_lang")],
            [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")],
            [InlineKeyboardButton(text=f"✅ الطلبات المكتملة: {completed_orders}", callback_data="orders_info")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def send_welcome(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    
    unsubscribed = await get_unsubscribed_channels(user_id)
    
    if unsubscribed:
        keyboard_buttons = []
        for ch in unsubscribed:
            keyboard_buttons.append([InlineKeyboardButton(text=f"📢 اشترك في القناة @{ch['name']}", url=ch['url'])])
        
        keyboard_buttons.append([InlineKeyboardButton(text="🔄 تحقق من الاشتراك", callback_data="check_subscription")])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await message.answer(
            "❌ **عذراً، يبدو أنك غادرت إحدى القنوات المطلوبة!\nيرجى إعادة الاشتراك في القناة أدناه ثم اضغط على زر التحقق:**",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return

    if user_id in user_languages:
        lang = user_languages[user_id]
        text = "🚀 أهلاً بك من جديد في بوت تخطي مفاتيح دلتا:" if lang == "ar" else "🚀 Welcome back to Delta Key Bypasser bot:"
        await message.answer(text, reply_markup=get_main_menu(lang))
    else:
        lang_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇮🇶 العربية", callback_data="lang_ar"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
            ]
        ])
        await message.answer(
            "👋 **مرحباً بك! يرجى اختيار لغتك المفضلة:\nWelcome! Please choose your preferred language:**",
            reply_markup=lang_keyboard
        )

@dp.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    unsubscribed = await get_unsubscribed_channels(user_id)
    
    if unsubscribed:
        keyboard_buttons = []
        for ch in unsubscribed:
            keyboard_buttons.append([InlineKeyboardButton(text=f"📢 اشترك في القناة @{ch['name']}", url=ch['url'])])
        
        keyboard_buttons.append([InlineKeyboardButton(text="🔄 تحقق من الاشتراك", callback_data="check_subscription")])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        try:
            await callback.message.edit_text(
                "❌ **لم تقم بالاشتراك في القناة المطلوبة بعد!**",
                reply_markup=markup,
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await callback.answer("❌ لم تقم بالاشتراك بعد!", show_alert=True)
    else:
        lang_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇮🇶 العربية", callback_data="lang_ar"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
            ]
        ])
        try:
            await callback.message.edit_text(
                "✅ **تم التحقق بنجاح!\nيرجى اختيار لغتك المفضلة / Please choose your preferred language:**",
                reply_markup=lang_keyboard,
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await callback.answer("✅ شكراً لك!", show_alert=True)

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    user_languages[user_id] = lang
    
    text = "🚀 أهلاً بك في بوت تخطي مفاتيح دلتا. اختر ما تحتاجه من الأزرار أدناه:" if lang == "ar" else "🚀 Welcome to Delta Key Bypasser bot. Choose what you need from the buttons below:"
    
    try:
        await callback.message.edit_text(text, reply_markup=get_main_menu(lang))
    except Exception:
        pass
    await callback.answer()

@dp.callback_query(F.data == "change_lang")
async def change_language_prompt(callback: CallbackQuery):
    lang_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇮🇶 العربية", callback_data="lang_ar"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ])
    try:
        await callback.message.edit_text(
            "🌐 **اختر لغتك المفضلة / Choose your language:**",
            reply_markup=lang_keyboard
        )
    except Exception:
        pass
    await callback.answer()

@dp.callback_query(F.data == "bypass_link")
async def bypass_prompt(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_languages.get(user_id, "ar")
    
    back_text = "🔙 رجوع للقائمة" if lang == "ar" else "🔙 Back to Menu"
    prompt_text = "⚡️ **أرسل رابط Delta الآن في المحادثة وسأقوم بجلب المفتاح لك!**" if lang == "ar" else "⚡️ **Send the Delta link now in the chat and I will get the key for you!**"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=back_text, callback_data="back_to_menu")]
    ])
    try:
        await callback.message.edit_text(prompt_text, reply_markup=keyboard)
    except Exception:
        pass
    await callback.answer()

@dp.callback_query(F.data == "orders_info")
async def orders_info_callback(callback: CallbackQuery):
    await callback.answer(f"📊 إجمالي عدد الطلبات الناجحة والمكتملة في البوت هو: {completed_orders}", show_alert=True)

@dp.callback_query(F.data.startswith("ratings_page_"))
async def show_ratings_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    total_ratings = len(bot_ratings)
    
    if total_ratings == 0:
        ratings_text = "⭐ **لا توجد تقييمات حتى الآن.**"
        page = 0
    else:
        page = page % total_ratings
        r = bot_ratings[page]
        ratings_text = f"👤 **اسم الشخص:** {r['name']} 🇰🇰\n⭐ **التقييم:** {r['stars']}\n💬 **الوصف:** {r['text']}"

    next_page = (page + 1) % total_ratings if total_ratings > 0 else 0
    prev_page = (page - 1) % total_ratings if total_ratings > 0 else 0

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ أضف تقييمك", callback_data="add_rating")],
        [
            InlineKeyboardButton(text="⟨ السابق", callback_data=f"ratings_page_{prev_page}"),
            InlineKeyboardButton(text="التالي ⟩", callback_data=f"ratings_page_{next_page}")
        ],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])
    
    try:
        await callback.message.edit_text(ratings_text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()

@dp.callback_query(F.data == "add_rating")
async def add_rating_prompt(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 ⭐", callback_data="rate_1"),
            InlineKeyboardButton(text="2 ⭐", callback_data="rate_2"),
            InlineKeyboardButton(text="3 ⭐", callback_data="rate_3"),
            InlineKeyboardButton(text="4 ⭐", callback_data="rate_4"),
            InlineKeyboardButton(text="5 ⭐", callback_data="rate_5")
        ],
        [InlineKeyboardButton(text="🔙 إلغاء", callback_data="ratings_page_0")]
    ])
    try:
        await callback.message.edit_text("⭐ **اختر من 1 إلى 5 نجوم لتقييم البوت:**", reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()

@dp.callback_query(F.data.startswith("rate_"))
async def process_star_rating(callback: CallbackQuery, state: FSMContext):
    stars_count = callback.data.split("_")[1]
    stars_str = "⭐" * int(stars_count)
    
    await state.update_data(stars=stars_str)
    await state.set_state(RatingStates.waiting_for_review_text)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 إلغاء", callback_data="ratings_page_0")]
    ])
    
    try:
        await callback.message.edit_text(
            f"لقد اخترت {stars_count} نجوم ⭐\n\n✍️ **أرسل الآن وصف التقييم (رسالة نصية فقط):**",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()

@dp.message(RatingStates.waiting_for_review_text, F.text & ~F.text.startswith("/"))
async def save_user_review(message: Message, state: FSMContext):
    data = await state.get_data()
    stars = data.get("stars", "⭐⭐⭐⭐⭐")
    review_text = message.text.strip()
    user_name = message.from_user.first_name
    
    bot_ratings.append({"name": user_name, "stars": stars, "text": review_text})
    save_ratings()
    
    await state.clear()
    
    await message.answer("✅ **تم حفظ تقييمك بنجاح، شكراً لك!**", parse_mode="Markdown")
    
    last_page = len(bot_ratings) - 1
    r = bot_ratings[last_page]
    ratings_text = f"👤 **اسم الشخص:** {r['name']} 🇰🇰\n⭐ **التقييم:** {r['stars']}\n💬 **الوصف:** {r['text']}"
    
    next_page = (last_page + 1) % len(bot_ratings)
    prev_page = (last_page - 1) % len(bot_ratings)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ أضف تقييمك", callback_data="add_rating")],
        [
            InlineKeyboardButton(text="⟨ السابق", callback_data=f"ratings_page_{prev_page}"),
            InlineKeyboardButton(text="التالي ⟩", callback_data=f"ratings_page_{next_page}")
        ],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ])
    await message.answer(ratings_text, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_languages.get(user_id, "ar")
    
    about_text = "هذا البوت مخصص لتخطي روابط ومفاتيح دلتا بكفاءة وسرعة عالية." if lang == "ar" else "This bot is designed to bypass Delta links and keys efficiently and quickly."
    
    try:
        await callback.message.edit_text(about_text, reply_markup=get_main_menu(lang))
    except Exception:
        pass
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    lang = user_languages.get(user_id, "ar")
    
    menu_text = "مرحباً بك من جديد! اختر ما تحتاجه:" if lang == "ar" else "Welcome back! Choose what you need:"
    
    try:
        await callback.message.edit_text(menu_text, reply_markup=get_main_menu(lang))
    except Exception:
        pass
    await callback.answer()

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_user_links(message: Message):
    global completed_orders
    user_id = message.from_user.id

    unsubscribed = await get_unsubscribed_channels(user_id)
    if unsubscribed:
        keyboard_buttons = []
        for ch in unsubscribed:
            keyboard_buttons.append([InlineKeyboardButton(text=f"📢 اشترك في القناة @{ch['name']}", url=ch['url'])])
        keyboard_buttons.append([InlineKeyboardButton(text="🔄 تحقق من الاشتراك", callback_data="check_subscription")])
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await message.answer("❌ **يجب عليك الاشتراك في القناة التي غادرتها أولاً لتتمكن من استخدام البوت!**", reply_markup=markup, parse_mode="Markdown")
        return

    lang = user_languages.get(user_id, "ar")
    text = message.text.strip()
    
    if "http" in text:
        init_wait = "⚡️ جار معالجة رابطك\nالمحاولة 1/3\n\n`█▒▒▒▒▒▒▒▒▒` **10%**" if lang == "ar" else "⚡️ Processing your link\nAttempt 1/3\n\n`█▒▒▒▒▒▒▒▒▒` **10%**"
        processing_msg = await message.answer(init_wait, parse_mode="Markdown")
        
        try:
            await asyncio.sleep(0.8)
            mid_wait1 = "⚡️ جار فحص وتحقيق الرابط...\n\n`████▒▒▒▒▒▒` **40%**" if lang == "ar" else "⚡️ Checking and verifying link...\n\n`████▒▒▒▒▒▒` **40%**"
            await processing_msg.edit_text(mid_wait1, parse_mode="Markdown")

            await asyncio.sleep(0.8)
            mid_wait2 = "⚡️ جار تجاوز الخطوات النهائية...\n\n`████████▒▒` **75%**" if lang == "ar" else "⚡️ Bypassing final steps...\n\n`████████▒▒` **75%**"
            await processing_msg.edit_text(mid_wait2, parse_mode="Markdown")

            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, params={"url": text}, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        key = data.get("key")
                        error = data.get("error")
                        times = data.get("times")
                        cached = data.get("cached", False)
                        
                        await asyncio.sleep(0.5)
                        
                        if key:
                            completed_orders += 1
                            
                            if lang == "ar":
                                cache_text = " (من التخزين المؤقت ⚡️)" if cached else f" (الوقت: {times})"
                                success_msg = f"---------------- 100%\n\nتم التجاوز بنجاح ✅\n\nالمفتاح: 🔑{cache_text}\n`{key}`"
                                btn_copy = "📋 نسخ المفتاح"
                                btn_ext = "🔗 رابط الاستخراج"
                            else:
                                cache_text = " (From Cache ⚡️)" if cached else f" (Time: {times})"
                                success_msg = f"---------------- 100%\n\nBypass successful ✅\n\nKey: 🔑{cache_text}\n`{key}`"
                                btn_copy = "📋 Copy Key"
                                btn_ext = "🔗 Extraction Link"
                            
                            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text=btn_copy, copy_text=CopyTextButton(text=str(key)))],
                                [InlineKeyboardButton(text=btn_ext, url=text)]
                            ])
                            
                            await processing_msg.edit_text(success_msg, parse_mode="Markdown", reply_markup=keyboard)
                        else:
                            err_text = f"❌ **فشل التخطي:**\n`{error}`" if lang == "ar" else f"❌ **Bypass failed:**\n`{error}`"
                            await processing_msg.edit_text(err_text, parse_mode="Markdown")
                    else:
                        err_status = f"❌ حدث خطأ في استجابة السيرفر (كود: {response.status})" if lang == "ar" else f"❌ Server response error (Code: {response.status})"
                        await processing_msg.edit_text(err_status)
        except Exception as e:
            err_conn = f"❌ حدث خطأ أثناء الاتصال بالسيرفر المحلي:\n`{str(e)}`" if lang == "ar" else f"❌ Error connecting to local server:\n`{str(e)}`"
            await processing_msg.edit_text(err_conn, parse_mode="Markdown")
    else:
        msg_valid = "يرجى إرسال رابط صالح يبدأ بـ http." if lang == "ar" else "Please send a valid link starting with http."
        await message.answer(msg_valid)

async def main():
    start_local_server()
    await asyncio.sleep(2)
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 بوت تيليجرام يعمل الآن والسيرفر يعمل معه في الخلفية...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        if server_process:
            server_process.terminate()
