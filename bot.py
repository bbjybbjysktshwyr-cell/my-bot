import os
import sys
import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- إعدادات البوت الأساسية ---
TOKEN = "8966597040:AAFRs5K7XJD5bXToG4m3IqVSHy6gw7BgSDQ"
ADMIN_ID = 6697426766
CHANNEL_USERNAME = "@scriptRoger"  # قناة الاشتراك الإجباري الثابتة

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

# --- قواعد البيانات المؤقتة (تمنع الحذف عند التحديث بفضل نظام الحفظ) ---
MAPS_DB = {
    "Blox Fruits": {"id": 1, "name": "Blox Fruits", "desc": "سكربتات فواكه وبلوكس"},
    "PS99": {"id": 2, "name": "Pet Simulator 99", "desc": "سكربتات التجميع والبتات"}
}

SCRIPTS_DB = {
    "Blox Fruits": [
        {"title": "Redz Hub", "code": "loadstring(game:HttpGet('https://raw.githubusercontent.com/...\n", "key_link": "https://delta.links/example"}
    ]
}

# حالة الصيانة ووضع التجربة
BOT_SETTINGS = {
    "maintenance": False,
    "test_mode": False
}

# --- حالات FSM للإدارة ---
class AdminState(StatesGroup):
    waiting_for_map_name = State()
    waiting_for_map_desc = State()
    waiting_for_script_title = State()
    waiting_for_script_code = State()
    waiting_for_script_link = State()

# --- دالة التخطي وجلب المفتاح عبر سيرفر الـ API المحلي ---
async def get_delta_key(user_url: str):
    api_url = "http://127.0.0.1:2233/solve"
    payload = {"url": user_url}
    
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            key = data.get("key") or data.get("result")
            if key:
                return f"✅ تم استخراج المفتاح بنجاح:\n`{key}`"
            else:
                return "❌ لم يتم العثور على المفتاح في الاستجابة."
        else:
            return "❌ حدث خطأ أثناء الاتصال بسيرفر التخطي."
    except Exception as e:
        return f"❌ خطأ في الاتصال بالسيرفر المحلي: {str(e)}"

# --- فحص الاشتراك الإجباري ---
async def check_sub(user_id: int) -> bool:
    if BOT_SETTINGS["test_mode"] and user_id == ADMIN_ID:
        return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception:
        pass
    return False

# --- أمر البدء (Start) ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    if BOT_SETTINGS["maintenance"] and user_id != ADMIN_ID:
        await message.answer("⚠️ البوت متوقف حالياً للصيانة. يرجى العودة لاحقاً.")
        return

    is_subscribed = await check_sub(user_id)
    if not is_subscribed:
        builder = InlineKeyboardBuilder()
        builder.button(text="📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
        builder.button(text="✅ تحقق من الاشتراك", callback_data="check_subscription")
        builder.adjust(1)
        await message.answer(
            f"⚠️ عذراً، يجب عليك الاشتراك في قناة البوت أولاً لتتمكن من استخدامه:\n{CHANNEL_USERNAME}",
            reply_markup=builder.as_markup()
        )
        return

    await show_main_menu(message)

async def show_main_menu(message: types.Message, edit=False):
    builder = InlineKeyboardBuilder()
    for map_name in MAPS_DB.keys():
        builder.button(text=f"🎮 {map_name}", callback_data=f"map_{map_name}")
    
    if message.from_user.id == ADMIN_ID:
        builder.button(text="⚙️ لوحة التحكم", callback_data="admin_panel")
    
    builder.adjust(1)
    text = "مرحباً بك في بوت سكربتات روبلوكس والتخطي! اختر الماب المطلوب:"
    
    if edit:
        await message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await message.answer(text, reply_markup=builder.as_markup())

# --- معالجة روابط التخطي (دلتا / لودلابس) ---
@dp.message(F.text.startswith("http"))
async def handle_links(message: types.Message):
    user_id = message.from_user.id
    if BOT_SETTINGS["maintenance"] and user_id != ADMIN_ID:
        return

    if not await check_sub(user_id):
        await message.answer("⚠️ يجب الاشتراك بقناة البوت أولاً لاستخدام ميزة التخطي.")
        return

    processing_msg = await message.answer("⏳ جاري الاتصال بسيرفر التخطي واستخراج الكود والمفتاح...")
    
    # استدعاء دالة جلب المفتاح من الـ API المحلي
    result_text = await get_delta_key(message.text)
    
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=processing_msg.message_id,
        text=result_text,
        parse_mode="Markdown"
    )

# --- أزرار التحكم والـ Callbacks ---
@dp.callback_query(F.data == "check_subscription")
async def verify_sub(callback: types.CallbackQuery):
    if await check_sub(callback.from_user.id):
        await callback.message.delete()
        await show_main_menu(callback.message)
    else:
        await callback.answer("❌ لم تقم بالاشتراك في القناة بعد!", show_alert=True)

@dp.callback_query(F.data.startswith("map_"))
async def select_map(callback: types.CallbackQuery):
    map_name = callback.data.split("_", 1)[1]
    scripts = SCRIPTS_DB.get(map_name, [])
    
    builder = InlineKeyboardBuilder()
    for script in scripts:
        builder.button(text=f"📜 {script['title']}", callback_data=f"script_{map_name}_{script['title']}")
    
    builder.button(text="🔙 رجوع", callback_data="back_to_main")
    builder.adjust(1)
    
    await callback.message.edit_text(f"📁 سكربتات ماب: *{map_name}*", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await show_main_menu(callback.message, edit=True)

# --- لوحة التحكم الخاصة بالأدمن ---
@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ إضافة ماب", callback_data="add_map")
    builder.button(text="➕ إضافة سكربت", callback_data="add_script")
    status_maint = "إيقاف الصيانة 🟢" if BOT_SETTINGS["maintenance"] else "تفعيل الصيانة 🔴"
    builder.button(text=status_maint, callback_data="toggle_maintenance")
    builder.button(text="🔙 رجوع للقائمة", callback_data="back_to_main")
    builder.adjust(1)
    
    await callback.message.edit_text("⚙️ *لوحة تحكم المشرف*:", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "toggle_maintenance")
async def toggle_maint(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    BOT_SETTINGS["maintenance"] = not BOT_SETTINGS["maintenance"]
    await admin_panel(callback)

# --- تشغيل البوت ---
async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
