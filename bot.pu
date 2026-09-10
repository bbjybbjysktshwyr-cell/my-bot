import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8815004150:AAEO-paQOWRnQ88w_tSKHyG71TA37ndF1xg"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# دالة لتصميم القائمة الرئيسية مثل الصورة
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 تجاوز رابط", callback_data="bypass_menu")
    builder.button(text="🎮 سكريبتات و هاكات", callback_data="scripts_menu")
    builder.button(text="❓ الروابط المدعومة", callback_data="supported_links")
    builder.button(text="📖 شرح البوت", callback_data="bot_help")
    builder.button(text="⭐ تقييمات البوت", callback_data="bot_rating")
    builder.button(text="🌐 تغيير اللغة", callback_data="change_lang")
    builder.button(text="✅ الطلبات المتكاملة: 24941", callback_data="stats")
    builder.adjust(1) # ترتيب الأزرار تحت بعضها
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "مرحباً بك في بوت تجاوز الروابط الاحترافي! 👋\n\n"
        "اختر القسم الذي ترغب به من الأسفل:"
    )
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())

# التعامل مع ضغط الأزرار التفاعلية
@dp.callback_query(F.data == "bypass_menu")
async def bypass_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🗂️ **أرسل الرابط المراد تجاوزه الآن في الدرشة:**",
        reply_markup=InlineKeyboardBuilder().button(text="🔙 رجوع للقائمة", callback_data="back_home").as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data == "back_home")
async def back_home_handler(callback: types.CallbackQuery):
    welcome_text = (
        "مرحباً بك في بوت تجاوز الروابط الاحترافي! 👋\n\n"
        "اختر القسم الذي ترغب به من الأسفل:"
    )
    await callback.message.edit_text(welcome_text, reply_markup=main_menu_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "scripts_menu")
async def scripts_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎮 قسم السكريبتات والهاكات قيد التحديث...\nانتظرنا في التحديثات القادمة!",
        reply_markup=InlineKeyboardBuilder().button(text="🔙 رجوع للقائمة", callback_data="back_home").as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data == "supported_links")
async def supported_handler(callback: types.CallbackQuery):
    text = "🌐 الروابط المدعومة حالياً:\n- LootLabs\n- Boosty\n- Linkvertise"
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardBuilder().button(text="🔙 رجوع للقائمة", callback_data="back_home").as_markup()
    )
    await callback.answer()

if __name__ == "__main__":
    import asyncio
    print("🚀 البوت الاحترافي يعمل الآن...")
    asyncio.run(dp.start_polling(bot))
