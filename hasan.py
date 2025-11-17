import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import BaseFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

CHANNELS = ["@mrxakimoff_eftbl", "@hasantojiqulovoffical"]
warned_users = set()

def subscription_keyboard():
    builder = InlineKeyboardBuilder()
    for i, channel in enumerate(CHANNELS, 1):
        builder.row(
            InlineKeyboardButton(
                text=f"📢 Kanal {i} ga obuna bo‘lish",
                url=f"https://t.me/{channel[1:]}"
            )
        )
    builder.row(InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="sub_confirm"))
    return builder.as_markup()

class AdvertisementFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        if message.content_type in [
            types.ContentType.PHOTO, types.ContentType.VIDEO,
            types.ContentType.DOCUMENT, types.ContentType.ANIMATION,
            types.ContentType.VIDEO_NOTE, types.ContentType.STICKER
        ]:
            return True
        if message.text and ("t.me/" in message.text or "http" in message.text):
            return True
        return False

async def check_subscription_status(user_id: int):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# 🔹 Guruhga yangi foydalanuvchi qo‘shilganda xush kelibsiz
async def welcome_new_members(message: types.Message):
    for user in message.new_chat_members:
        await message.reply(
            f"👋 Salom, {user.full_name}! Guruhga xush kelibsiz!\n"
            f"🚨 Guruhda reklama yuborish uchun quyidagi kanallarga obuna bo‘lishingiz shart.",
            reply_markup=subscription_keyboard()
        )

dp.message.register(welcome_new_members, content_types=types.ContentType.NEW_CHAT_MEMBERS)

# 🔹 Reklama yuborilsa tekshiradi
async def check_subscription(message: types.Message):
    user_id = message.from_user.id
    is_sub = await check_subscription_status(user_id)
    if not is_sub:
        await message.delete()
        if user_id not in warned_users:
            warned_users.add(user_id)
            await message.answer(
                "🚫 Reklama ruxsat etilmagan! Majburiy kanallarga obuna bo‘ling!",
                reply_markup=subscription_keyboard()
            )
    else:
        warned_users.discard(user_id)

dp.message.register(check_subscription, AdvertisementFilter())

# 🔹 Obuna tasdiqlash tugmasi
async def sub_confirm(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_sub = await check_subscription_status(user_id)
    if is_sub:
        warned_users.discard(user_id)
        await callback.message.edit_text(
            "✅ Ruxsat berildi, endi reklama yuborishingiz mumkin!"
        )
    else:
        await callback.answer("⚠️ Hali ham barcha kanallarga obuna emassiz!", show_alert=True)

dp.callback_query.register(sub_confirm, lambda c: c.data == "sub_confirm")

if __name__ == "__main__":
    print("🤖 Bot ishlayapti...")
    asyncio.run(dp.start_polling(bot))
