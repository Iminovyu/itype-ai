import logging, asyncio, requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from langdetect import detect
from config import BOT_TOKEN, AUTH_TOKEN, API_URL, MISTRAL_MODEL
from db import *

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

lang_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
     InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
])

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Я бот с ИИ. Напиши что-нибудь, и я тебе отвечу!")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("/start — начать\n/stop — завершить диалог\n/reset — очистить всё\n/history — список\n/history N — диалог\n/lang — язык")

@dp.message(Command("stop"))
async def cmd_stop(message: Message):
    stop_session(message.from_user.id)
    await message.answer("✅ Текущий диалог завершён.")

@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    reset_history(message.from_user.id)
    await message.answer("🗑 История удалена.")

@dp.message(Command("history"))
async def cmd_history(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    sessions = get_user_sessions(user_id)
    if len(args) == 1:
        if not sessions:
            await message.answer("📭 История пуста.")
        else:
            reply = "\n".join([f"{i+1}. {title} ({created})" for i, (sid, title, created) in enumerate(sessions)])
            await message.answer(f"📜 История:\n{reply}\n\n/history N — чтобы открыть")
    else:
        try:
            index = int(args[1]) - 1
            session_id = sessions[index][0]
            msgs = get_session_messages(session_id)
            reply = ""
            for m in msgs:
                prefix = "👤" if m["role"] == "user" else "🤖"
                reply += f"{prefix} {m['content']}\n\n"
            await message.answer(reply or "⛔️ Нет сообщений.")
        except:
            await message.answer("❌ Укажи номер из /history")

@dp.message(Command("lang"))
async def cmd_lang(message: Message):
    await message.answer("Выберите язык:", reply_markup=lang_markup)

@dp.callback_query()
async def lang_handler(callback: CallbackQuery):
    await callback.answer("⚙️ Язык определяется автоматически.")

@dp.message()
async def handle_message(message: Message):
    if not message.text:
        return await message.answer("Пожалуйста, отправь текст.")
    
    text = message.text.strip()
    user_id = message.from_user.id

    try:
        lang = detect(text)
    except:
        lang = "en"

    system_prompt = "Всегда отвечай на русском языке." if lang == "ru" else "Always reply in English."
    save_message(user_id, "user", text)

    session_id = get_session(user_id)
    if session_id:
        history = get_session_messages(session_id)
    else:
        history = [{"role": "user", "content": text}]

    response = await ask_model(history, system_prompt)
    save_message(user_id, "assistant", response)
    await message.answer(response)

async def ask_model(messages, system_instruction: str) -> str:
    headers = {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "model": MISTRAL_MODEL,
        "messages": [{"role": "system", "content": system_instruction}] + messages
    }
    try:
        resp = await asyncio.to_thread(lambda: requests.post(API_URL, headers=headers, json=payload, timeout=15))
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        return "⚠️ Произошла ошибка при запросе."

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
