import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# التوكن الخاص بك
TOKEN = "8815004150:AAEO-paQOWRnQ88w_tSKHyG71TA37ndF1xg"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  await message.answer(
      "أهلاً بك! أرسل لي أي رابط وسأقوم بمحاولة تجاوزه لك عبر keybypass.net."
  )


@dp.message()
async def handle_url(message: types.Message):
  user_url = message.text.strip()

  if not user_url.startswith("http"):
    await message.answer("يرجى إرسال رابط صالح يبدأ بـ http أو https.")
    return

  msg = await message.answer("جاري معالجة الرابط عبر keybypass.net... ⏳")

  try:
    # إرسال الرابط إلى الموقع
    api_url = f"https://keybypass.net/api?url={user_url}"

    async with aiohttp.ClientSession() as session:
      async with session.get(api_url, timeout=15) as response:
        if response.status == 200:
          # محاولة قراءة الاستجابة كـ JSON أو نص
          try:
            data = await response.json()
            bypassed_url = (
                data.get("result") or data.get("url") or str(data)
            )
          except:
            bypassed_url = await response.text()

          await msg.edit_text(f"تم التجاوز بنجاح! ✅\n\nالرابط الأصلي:\n{bypassed_url}")
        else:
          await msg.edit_text("حدث خطأ من الموقع، رمز الاستجابة غير صحيح.")
  except Exception as e:
    await msg.edit_text(f"حدث خطأ أثناء الاتصال: {str(e)}")


async def main():
  await dp.start_polling(bot)


if __name__ == "__main__":
  import asyncio

  asyncio.run(main())
