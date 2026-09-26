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

TOKEN = "8860565104:AAEVEX4ODFumP981Sto89sCZZmOe7MSHtzU"

# الآيدي الخاص بك فقط للتحكم
ADMIN_ID = 6697426766

API_URL = "http://127.0.0.1:2233/delta"

bot = Bot(token=TOKEN)
dp = Dispatcher()

RATINGS_FILE = "ratings.json"
SETTINGS_FILE = "settings.json"

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

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "maintenance_mode": False,
        "maintenance_text": "🛠 **البوت متوقف حالياً للصيانة والتحديث.**\nيرجى المحاولة لاحقاً.",
        "channels": []
    }

def save_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(admin_settings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في حفظ الإعدادات: {e}")

user_languages = {}
bot_ratings = load_ratings()
admin_settings = load_settings()
completed_orders = 0

class AdminStates(StatesGroup):
    waiting_for_channel = State()
    waiting_for_maintenance_text = State()

class RatingStates(StatesGroup):
    waiting_for_review_text = State()

server_process = None

def start_local_server():
    global server_process
    if server_process is None:
        server_process = subprocess.Popen(["python", "server.py", "--port", "2233"])
        print("🚀 تم تشغيل سيرفر دلتا المحلي تلقائياً في الخلفية...")

async def check_forced_subscription(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    
    for channel in admin_settings["channels"]:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True

def get_main_menu(lang="ar", is_admin=False):
    global completed_orders
    if lang == "en":
        keyboard = [
            [InlineKeyboardButton(text="⚡️ Bypass Delta Link", callback_data="bypass_link")],
            [InlineKeyboardButton(text="⭐ Bot Ratings 🟢", callback_data="ratings_page_0")],
            [InlineKeyboardButton(text="🌐 Change Language", callback_data="change_lang")],
            [InlineKeyboardButton(text="ℹ️ About Bot", callback_data="about")],
            [InlineKeyboardButton(text=f"✅ Completed Orders: {completed_orders}", callback_data="orders_info")]
        ]
        if is_admin:
            keyboard.append([InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    else:
        keyboard = [
            [InlineKeyboardButton(text="⚡️ تجاوز رابط دلتا", callback_data="bypass_link")],
            [InlineKeyboardButton(text="⭐ تقييمات البوت 🟢", callback_data="ratings_page_0")],
            [InlineKeyboardButton(text="🌐 تغيير اللغة", callback_data="change_lang")],
            [InlineKeyboardButton(text="ℹ️ حول البوت", callback_data="about")],
            [InlineKeyboardButton(text=f"✅ الطلبات المكتملة: {completed_orders}", callback_data="orders_info")]
        ]
        if is_admin:
            keyboard.append([InlineKeyboardButton(text="⚙️ لوحة التحكم", callback_data="admin_panel")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def send_welcome(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    is_admin = (user_id == ADMIN_ID)

    if admin_settings["maintenance_mode"] and not is_admin:
        await message.answer(admin_settings["maintenance_text"], parse_mode="Markdown")
        return

    if not await check_forced_subscription(user_id):
        sub_keyboard_list = []
        for ch in admin_settings["channels"]:
            sub_keyboard_list.append([InlineKeyboardButton(text=f"📢 اضغط للاشتراك في القناة", url=f"https://t.me/{ch.replace('@', '')}")])
        sub_keyboard_list.append([InlineKeyboardButton(text="🔄 تحقق من الاشتراك", callback_data="check_sub")])
        
        await message.answer(
            "⚠️ **عذراً، يجب عليك الاشتراك في قناة البوت لتتمكن من استخدامه!**\n\nقم بالاشتراك ثم اضغط على زر التحقق أدناه:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=sub_keyboard_list),
            parse_mode="Markdown"
        )
        return

    if user_id in user_languages:
        lang = user_languages[user_id]
        text = "🚀 أهلاً بك من جديد في بوت تخطي مفاتيح دلتا:" if lang == "ar" else "🚀 Welcome back to Delta Key Bypasser bot:"
        await message.answer(text, reply_markup=get_main_menu(lang, is_admin))
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

@dp.callback_query(F.data == "check_sub")
async def verify_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await check_forced_subscription(user_id):
        await callback.message.delete()
        lang = user_languages.get(user_id, "ar")
        is_admin = (user_id == ADMIN_ID)
        await callback.message.answer(
            "✅ شكراً لاشتراكك! يمكنك استخدام البوت الآن:",
            reply_markup=get_main_menu(lang, is_admin)
        )
    else:
        await callback.answer("❌ لم تقم بالاشتراك في جميع القنوات المطلوبة بعد!", show_alert=True)

@dp.callback_query(F.data == "admin_panel")
async def admin_panel_handler(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("عذراً، هذا الزر مخصص للأدمن فقط.", show_alert=True)
        return

    status_mode = "🟢 مفعل" if admin_settings["maintenance_mode"] else "🔴 معطل"
    channels_list = "\n".join([f"• {ch}" for ch in admin_settings["channels"]]) if admin_settings["channels"] else "لا توجد قنوات مضافة"

    text = (
        f"⚙️ **لوحة تحكم الأدمن:**\n\n"
        f"🛠 **وضع الصيانة:** {status_mode}\n"
        f"📢 **قنوات الاشتراك الإجباري:\n{channels_list}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 تبديل وضع الصيانة (تشغيل/إيقاف)", callback_data="toggle_maintenance")],
        [InlineKeyboardButton(text="✍️ تعديل رسالة الصيانة", callback_data="edit_maint_text")],
        [InlineKeyboardButton(text="➕ إضافة قناة اشتراك إجباري", callback_data="add_channel")],
        [InlineKeyboardButton(text="➖ حذف جميع القنوات", callback_data="clear_channels")],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة الرئيسية", callback_data="back_to_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "toggle_maintenance")
async def toggle_maintenance(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    admin_settings["maintenance_mode"] = not admin_settings["maintenance_mode"]
    save_settings()
    await admin_panel_handler(callback)

@dp.callback_query(F.data == "edit_maint_text")
async def edit_maint_text_prompt(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.waiting_for_maintenance_text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 إلغاء", callback_data="admin_panel")]
    ])
    await callback.message.edit_text(
        "✍️ **أرسل الآن نص رسالة الصيانة الجديد (يدعم Markdown):**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(AdminStates.waiting_for_maintenance_text, F.text)
async def save_maintenance_text(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    admin_settings["maintenance_text"] = message.text.strip()
    save_settings()
    await state.clear()
    await message.answer("✅ **تم تحديث رسالة الصيانة بنجاح وحفظها بشكل دائم!**", parse_mode="Markdown")

@dp.callback_query(F.data == "add_channel")
async def add_channel_prompt(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.waiting_for_channel)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 إلغاء", callback_data="admin_panel")]
    ])
    await callback.message.edit_text(
        "📢 **أرسل معرف القناة (يجب أن يبدأ بـ @ ويجب أن يكون البوت مشرفاً فيها):\nمثال:** `@MyChannel`",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(AdminStates.waiting_for_channel, F.text)
async def save_channel(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    channel_username = message.text.strip()
    if not channel_username.startswith("@"):
        await message.answer("❌ يرجى إرسال معرف صحيح يبدأ بـ `@` (مثال: `@ChannelName`)")
        return
    
    if channel_username not in admin_settings["channels"]:
        admin_settings["channels"].append(channel_username)
        save_settings()

    await state.clear()
    await message.answer(f"✅ **تمت إضافة وحفظ القناة {channel_username} بنجاح في القائمة الدائمة!**\n⚠️ تأكد من أن البوت مشرف في القناة ليعمل الفحص بشكل صحيح.", parse_mode="Markdown")

@dp.callback_query(F.data == "clear_channels")
async def clear_channels(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    admin_settings["channels"] = []
    save_settings()
    await callback.answer("🗑 تم حذف جميع قنوات الاشتراك الإجباري نهائياً.", show_alert=True)
    await admin_panel_handler(callback)

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    user_languages[user_id] = lang
    is_admin = (user_id == ADMIN_ID)
    
    text = "🚀 أهلاً بك في بوت تخطي مفاتيح دلتا. اختر ما تحتاجه من الأزرار أدناه:" if lang == "ar" else "🚀 Welcome to Delta Key Bypasser bot. Choose what you need from the buttons below:"
    
    await callback.message.edit_text(text, reply_markup=get_main_menu(lang, is_admin))
    await callback.answer()

@dp.callback_query(F.data == "change_lang")
async def change_language_prompt(callback: CallbackQuery):
    lang_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇮🇶 العربية", callback_data="lang_ar"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ])
    await callback.message.edit_text(
        "🌐 **اختر لغتك المفضلة / Choose your language:**",
        reply_markup=lang_keyboard
    )
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
    await callback.message.edit_text(prompt_text, reply_markup=keyboard)
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
    
    await callback.message.edit_text(ratings_text, reply_markup=keyboard, parse_mode="Markdown")
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
    await callback.message.edit_text("⭐ **اختر من 1 إلى 5 نجوم لتقييم البوت:**", reply_markup=keyboard, parse_mode="Markdown")
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
    
    await callback.message.edit_text(
        f"لقد اخترت {stars_count} نجوم ⭐\n\n✍️ **أرسل الآن وصف التقييم (رسالة نصية فقط):**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
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
    await message.answer(ratings_text, reply_markup=keyboard, parse_Mode="Markdown")

@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_languages.get(user_id, "ar")
    is_admin = (user_id == ADMIN_ID)
    
    about_text = "هذا البوت مخصص لتخطي روابط ومفاتيح دلتا بكفاءة وسرعة عالية." if lang == "ar" else "This bot is designed to bypass Delta links and keys efficiently and quickly."
    
    await callback.message.edit_text(about_text, reply_markup=get_main_menu(lang, is_admin))
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    lang = user_languages.get(user_id, "ar")
    is_admin = (user_id == ADMIN_ID)
    
    menu_text = "مرحباً بك من جديد! اختر ما تحتاجه:" if lang == "ar" else "Welcome back! Choose what you need:"
    
    await callback.message.edit_text(menu_text, reply_markup=get_main_menu(lang, is_admin))
    await callback.answer()

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_user_links(message: Message):
    global completed_orders
    user_id = message.from_user.id
    is_admin = (user_id == ADMIN_ID)

    if admin_settings["maintenance_mode"] and not is_admin:
        await message.answer(admin_settings["maintenance_text"], parse_mode="Markdown")
        return

    if not await check_forced_subscription(user_id):
        await message.answer("⚠️ عذراً، يجب عليك الاشتراك في قناة البوت أولاً لتتمكن من إرسال الروابط! اضغط /start للاشتراك.")
        return

    lang = user_languages.get(user_id, "ar")
    text = message.text.strip()
    
    if "http" in text:
        wait_text = "⏳ جاري التواصل مع السيرفر وتخطي الرابط..." if lang == "ar" else "⏳ Communicating with server and bypassing link..."
        processing_msg = await message.answer(wait_text)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, params={"url": text}, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        key = data.get("key")
                        error = data.get("error")
                        times = data.get("times")
                        cached = data.get("cached", False)
                        
                        if key:
                            completed_orders += 1
                            
                            if lang == "ar":
                                cache_text = " (من التخزين المؤقت ⚡️)" if cached else f" (الوقت: {times})"
                                success_msg = f"🎉 **تم بنجاح استخراج المفتاح!**{cache_text}\n\n`{key}`"
                                btn_text = "📋 اضغط هنا لنسخ الكود"
                            else:
                                cache_text = " (From Cache ⚡️)" if cached else f" (Time: {times})"
                                success_msg = f"🎉 **Key successfully extracted!**{cache_text}\n\n`{key}`"
                                btn_text = "📋 Click here to copy code"
                            
                            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text=btn_text, copy_text=CopyTextButton(text=key))]
                            ])
                            
                            await processing_msg.edit_text(success_msg, parse_mode="Markdown", reply_markup=keyboard)
                        else:
                            err_text = f"❌ **فشل التخطي:**\n`{error}`" if lang == "ar" else f"❌ **Bypass failed:**\n`{error}`"
                            await processing_msg.edit_text(err_text)
                    else:
                        err_status = f"❌ حدث خطأ في استجابة السيرفر (كود: {response.status})" if lang == "ar" else f"❌ Server response error (Code: {response.status})"
                        await processing_msg.edit_text(err_status)
        except Exception as e:
            err_conn = f"❌ حدث خطأ أثناء الاتصال بالسيرفر المحلي:\n`{str(e)}`" if lang == "ar" else f"❌ Error connecting to local server:\n`{str(e)}`"
            await processing_msg.edit_text(err_conn)
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
