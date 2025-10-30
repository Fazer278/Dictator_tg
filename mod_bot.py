# mod_bot.py — версия с восстановленным приветствием при добавлении в группу
import os
import re
import asyncio
import logging
from typing import Set
from telegram.ext import ChatMemberHandler
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------- Логирование ----------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ---------- Настройки ----------
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 1821129664  # твой Telegram ID

# начальные списки
blacklist: Set[str] = {"реклама", "ставки", "казино", "вк", "крипта"}
parts_blacklist: Set[str] = {"работ", "шабаш"}
whitelist: Set[int] = {OWNER_ID}

# кешированные паттерны (будем пересобирать при изменениях)
_exact_pattern = None  # compiled regex for exact blacklist words
_word_re = re.compile(r"\w+", flags=re.UNICODE)


def rebuild_exact_pattern():
    global _exact_pattern
    if not blacklist:
        _exact_pattern = None
    else:
        pattern = r"\b(" + "|".join(re.escape(w) for w in sorted(blacklist)) + r")\b"
        _exact_pattern = re.compile(pattern, flags=re.IGNORECASE | re.UNICODE)


# начальная сборка
rebuild_exact_pattern()


# ---------- Утилиты ----------
async def is_admin(user_id: int, chat) -> bool:
    """
    Асинхронно проверяет, является ли пользователь админом или владельцем
    """
    if user_id == OWNER_ID:
        return True
    try:
        member = await chat.get_member(user_id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        log.exception("is_admin: ошибка при получении участника: %s", e)
        return False


def contains_blacklisted_word(text: str) -> bool:
    """Проверка: точный матч по слову или по части (substring) в токене."""
    if not text:
        return False
    text_lower = text.lower()

    # 1) точный матч (слово)
    if _exact_pattern and _exact_pattern.search(text_lower):
        return True

    # 2) части — проверяем каждый токен
    if parts_blacklist:
        tokens = _word_re.findall(text_lower)
        for token in tokens:
            for part in parts_blacklist:
                if part and part in token:
                    return True
    return False


# ==============================
# Приветствие при добавлении бота
# ==============================
async def my_chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получаем событие изменения статуса бота в чате.
    Когда бот сам добавлен (новый статус member/administrator/creator) — шлём приветствие.
    """
    try:
        # update.my_chat_member присутствует для ChatMember updates
        new = update.my_chat_member.new_chat_member
        # проверим, что обновление относится к боту
        if new.user and new.user.is_bot:
            status = new.status  # например: 'member' или 'administrator'
            if status in ("member", "administrator", "creator"):
                chat = update.effective_chat
                text = (
                    f"👋 Ну чтож, видать в {chat.title} всё стало настолько плохо с мошенниками, "
                    "что ваше правительство соизволило позвать Меня!!!\n\n"
                    "Будем знакомы, Хуленсио Вингардио III, можно просто: Диктатор.\n"
                    "Меня зовут туда, где царит беззаконие капиталистического спама. Но не переживайте, став вашим Вождём я смогу привести это место в порядок\n"
                    "Вот мой первый указ: должность модератора упраздняется: вы мне будете нужны в комитете цензуры. Запретить или разрешить слово можно через встроенные команды. Я не люблю возиться со всеми этими директивами, извините.\n"
                    "Также вы можете создать элиту тех, на кого цензура действовать не будет (по умолчанию туда входят все сотрудники Комитета)\n"
                    "А если ты, гражданин заметил как кто-то обманывает систему и продолжает писать крамолу, немедленно свяжись с сотрудником Комитета цензуры (модератором)!\n"
                    "Полный список команд - /help\n\n"
                    "А теперь остались формальности. Назначьте меня своим диктатором, выдав права администратора."
                )
                await context.bot.send_message(chat_id=chat.id, text=text)
    except Exception as e:
        log.exception("my_chat_member_handler error: %s", e)


# ==============================
# 💬 Обработчики команд
# ==============================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        log.info("Help command from user %s in chat %s", update.effective_user.id, update.effective_chat.id if update.effective_chat else None)
    ...    
    await update.message.reply_text(
        "📋 Доступные команды:\n"
        "/help — показать это сообщение\n"
        "/blacklist — показать список запрещённых слов\n"
        "/addword <слово> — добавить слово в ЧС\n"
        "/delword <слово> — удалить слово из ЧС\n"
        "/listparts — показать части (substring)\n"
        "/addpart <кусок> — добавить кусок\n"
        "/delpart <кусок> — удалить кусок\n"
        "/whitelist — показать белый список\n"
        "/adduser <id> — добавить пользователя в whitelist\n"
        "/deluser <id> — удалить\n"
        "/unban <id> — разбанить пользователя"
    )


async def show_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not blacklist:
        await update.message.reply_text("ЧС пуст.")
    else:
        await update.message.reply_text("ЧС:\n" + "\n".join(sorted(blacklist)))


async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
        log.info("Add new word to blacklist from user %s in chat %s", update.effective_user.id, update.effective_chat.id if update.effective_chat else None)
    ...    
    if not await is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("Только админы могут менять ЧС.")
    if not context.args:
        return await update.message.reply_text("Использование: /addword <слово>")
    word = " ".join(context.args).strip().lower()
    blacklist.add(word)
    rebuild_exact_pattern()
    await update.message.reply_text(f"Добавлено: {word}")


async def del_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("Только админы могут менять ЧС.")
    if not context.args:
        return await update.message.reply_text("Использование: /delword <слово>")
    word = " ".join(context.args).strip().lower()
    blacklist.discard(word)
    rebuild_exact_pattern()
    await update.message.reply_text(f"Удалено: {word}")


async def list_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("Только админы.")
    if not parts_blacklist:
        return await update.message.reply_text("Частичные правила пусты.")
    await update.message.reply_text("Части:\n" + "\n".join(sorted(parts_blacklist)))


async def add_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def add_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
        log.info("Adding new part of ban word from user %s in chat %s", update.effective_user.id, update.effective_chat.id if update.effective_chat else None)
    ...    
    if not await is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("Только админы.")
    if not context.args:
        return await update.message.reply_text("Использование: /addpart <кусок>")
    part = context.args[0].lower().strip()
    parts_blacklist.add(part)
    await update.message.reply_text(f"Добавлен кусок: {part}")


async def del_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("Только админы.")
    if not context.args:
        return await update.message.reply_text("Использование: /delpart <кусок>")
    part = context.args[0].lower().strip()
    parts_blacklist.discard(part)
    await update.message.reply_text(f"Удалён кусок: {part}")


async def show_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("Только админы.")
    if not whitelist:
        return await update.message.reply_text("Whitelist пуст.")
    await update.message.reply_text("Whitelist:\n" + "\n".join(str(x) for x in sorted(whitelist)))


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("Только админы.")
    if not context.args:
        return await update.message.reply_text("Использование: /adduser <id>")
    try:
        uid = int(context.args[0])
        whitelist.add(uid)
        await update.message.reply_text(f"Добавлен в whitelist: {uid}")
    except ValueError:
        await update.message.reply_text("ID должен быть числом.")


async def del_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("Только админы.")
    if not context.args:
        return await update.message.reply_text("Использование: /deluser <id>")
    try:
        uid = int(context.args[0])
        whitelist.discard(uid)
        await update.message.reply_text(f"Удалён из whitelist: {uid}")
    except ValueError:
        await update.message.reply_text("ID должен быть числом.")


async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("Только админы.")
    if not context.args:
        return await update.message.reply_text("Использование: /unban <id>")
    try:
        uid = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, uid)
        await update.message.reply_text(f"Пользователь {uid} разбанен.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


# ==============================
# 🚫 Проверка сообщений
# ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return
    if not (msg.text or msg.caption):
        return

    text = (msg.text or msg.caption or "")
    user_id = msg.from_user.id

    # игнорируем whitelist и админов
    if user_id in whitelist:
        return
    if await is_admin(user_id, update.effective_chat):
        return

    if contains_blacklisted_word(text):
        try:
            await msg.delete()
            # бан и быстрая выгрузка (режим "kick")
            await update.effective_chat.ban_member(user_id)
            await update.effective_chat.unban_member(user_id)
            await update.message.reply_text(f"🚫 Сообщение удалено и пользователь исключён: {msg.from_user.full_name}")
            log.info("Заблокировано: %s — %s", user_id, text)
        except Exception as e:
            log.exception("Ошибка при бане/удалении: %s", e)


# ---------- Web server для keep-alive (aiohttp) ----------
async def web_root(request):
    return web.Response(text="ok")


async def start_keepalive_server(app_obj):
    # запускается через post_init
    runner = web.AppRunner(app_obj["web_app"])
    await runner.setup()
    port = int(os.getenv("PORT", "3000"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log.info("Keep-alive server started on port %s", port)


# ---------- Сборка Application и регистрация обработчиков ----------
def build_application():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не задан в окружении")

    app = ApplicationBuilder().token(TOKEN).build()

    # команды
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("blacklist", show_blacklist))
    app.add_handler(CommandHandler("addword", add_word))
    app.add_handler(CommandHandler("delword", del_word))

    app.add_handler(CommandHandler("listparts", list_parts))
    app.add_handler(CommandHandler("addpart", add_part))
    app.add_handler(CommandHandler("delpart", del_part))

    app.add_handler(CommandHandler("whitelist", show_whitelist))
    app.add_handler(CommandHandler("adduser", add_user))
    app.add_handler(CommandHandler("deluser", del_user))

    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    # добавляем приветствие, когда бота добавляют
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bot_added_to_group))
    app.add_handler(ChatMemberHandler(my_chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))    

    # post_init — запуск keep-alive сервера в фоновом таске
    async def _post_init(application):
        # создаём aiohttp web app и регистрируем маршрут
        web_app = web.Application()
        web_app.router.add_get("/", web_root)
        # кладём его в application (доступно в старте)
        application.bot_data["web_app"] = web_app
        # стартуем сервер
        asyncio.create_task(start_keepalive_server(application.bot_data))

    app.post_init = _post_init
    return app


# ---------- main ----------
if __name__ == "__main__":
    try:
        application = build_application()
        log.info("Запуск бота")
        application.run_polling()
    except Exception:
        log.exception("Ошибка при старте")