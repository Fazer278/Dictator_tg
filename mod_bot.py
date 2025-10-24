from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import re
import os

# ---- обработчик при добавлении в группу ----
async def bot_added_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat
    await update.message.reply_text(
        f"👋 Ну чтож, видать в {chat.title} всё стало настолько плохо с мошенниками, что ваше правительство соизволило позвать Меня!!!\n\n"
        "Будем знакомы, Хуленсио Вингардио III, можно просто: Диктатор.\n"
        "Меня зовут туда, где царит беззаконие капиталистического спама. Но не переживайте, став вашим Вождём я смогу привести это место в порядок\n"
        "Вот мой первый указ: должность модератора упраздняется: вы мне будете нужны в комитете цензуры. Запретить или разрешить слово можно через встроенные команды. Я не люблю возиться со всеми этими директивами, извините.\n"
        "Также вы можете создать элиту тех, на кого цензура действовать не будет (по умолчанию туда входят все сотрудники Комитета)\n"
        "А если ты, гражданин заметил как кто-то обманывает систему и продолжает писать крамолу, немедленно свяжись с сотрудником Комитета цензуры (модератором)!\n"
        "Полный список команд - /help\n\n"
        "А теперь остались формальности. Назначьте меня своим диктатором, выдав права администратора."
    )

# ==============================
# 🔧 Настройки
# ==============================
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 1821129664  # твой Telegram ID

# Чёрный список слов
blacklist = {"реклама", "ставки", "казино", "вк", "крипта"}

# Белый список пользователей
whitelist = {OWNER_ID}

# ==============================
# ⚙️ Вспомогательные функции
# ==============================
def is_admin(user_id: int, chat):
    """Проверяет, является ли пользователь админом или владельцем"""
    if user_id == OWNER_ID:
        return True
    try:
        member = chat.get_member(user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

def contains_blacklisted_word(text: str):
    """Проверяет, есть ли в тексте слова из чёрного списка"""
    text_lower = text.lower()
    for word in blacklist:
        if re.search(rf"\b{re.escape(word)}\b", text_lower):
            return True
    return False

# ==============================
# 💬 Обработчики команд
# ==============================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Доступные команды:*\n"
        "/help — показать это сообщение\n"
        "/blacklist — показать список запрещённых слов\n"
        "/addword <слово> — добавить слово в ЧС\n"
        "/delword <слово> — удалить слово из ЧС\n"
        "/whitelist — показать белый список\n"
        "/adduser <id> — добавить пользователя в белый список\n"
        "/deluser <id> — удалить пользователя из белого списка\n"
        "/unban <id> — разбанить пользователя",
        parse_mode="Markdown"
    )

async def show_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Пока что в чате действует полная свобода слова. Отставить политическую оттепель!" if not blacklist else "Список запрещённых слов\n" + "\n".join(blacklist)
    await update.message.reply_text(text)

async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("У вас нет необходимых полномочий")
    if not context.args:
        return await update.message.reply_text("Вы не указали запрещённое слово: /addword <слово>")
    word = context.args[0].lower()
    blacklist.add(word)
    await update.message.reply_text(f"Издан декрет о запрете слова: {word}")

async def del_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("У вас нет необходимых полномочий")
    if not context.args:
        return await update.message.reply_text("Вы не указали запрещенное слово: /delword <слово>")
    word = context.args[0].lower()
    if word in blacklist:
        blacklist.remove(word)
        await update.message.reply_text(f"Директива отменена: {word}")
    else:
        await update.message.reply_text("Вы ещё не запрещали это слово. Это можно исправить")

async def show_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "У вас пока нет элит" if not whitelist else "Элита:\n" + "\n".join(str(uid) for uid in whitelist)
    await update.message.reply_text(text)

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("У вас нет необходимых полномочий.")
    if not context.args:
        return await update.message.reply_text("Укажите ID гражданина: /adduser <id>")
    try:
        user_id = int(context.args[0])
        whitelist.add(user_id)
        await update.message.reply_text(f"Гражданин {user_id} добавлен в список элит.")
    except ValueError:
        await update.message.reply_text("ID должен быть числом.")

async def del_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("У вас нет необходимых полномочий.")
    if not context.args:
        return await update.message.reply_text("Укажите ID гражданина: /deluser <id>")
    try:
        user_id = int(context.args[0])
        if user_id in whitelist:
            whitelist.remove(user_id)
            await update.message.reply_text(f"Гражданин {user_id} разжалован и больше не является элитой. Гоните его! Насмехайтесь над ним!")
        else:
            await update.message.reply_text("Этот гражданин и так не имеет никаких преференций.")
    except ValueError:
        await update.message.reply_text("ID должен быть числом.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, update.effective_chat):
        return await update.message.reply_text("У вас нет необходимых полномочий.")
    if not context.args:
        return await update.message.reply_text("Укажите ID: /unban <id>")
    try:
        user_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f" Гражданин {user_id} реабилитирован. Прощайте, урановые рудники!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# ==============================
# 🚫 Проверка сообщений
# ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    user_id = msg.from_user.id

    # Игнорируем белый список
    if user_id in whitelist:
        return

    text = msg.text

    if contains_blacklisted_word(text):
        try:
            await msg.delete()
            await msg.chat.ban_member(user_id)
            await msg.chat.unban_member(user_id)
            await msg.reply_text(f"🚫 Сообщение от {msg.from_user.first_name} удалено за запрещённое слово.")
            print(f"❌ Заблокировано сообщение от {user_id}: {text}")
        except Exception as e:
            print(f"⚠️ Ошибка при удалении или бане: {e}")

# ==============================
# 🚀 Запуск
# ==============================
def build_app():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("blacklist", show_blacklist))
    app.add_handler(CommandHandler("addword", add_word))
    app.add_handler(CommandHandler("delword", del_word))
    app.add_handler(CommandHandler("whitelist", show_whitelist))
    app.add_handler(CommandHandler("adduser", add_user))
    app.add_handler(CommandHandler("deluser", del_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app


if __name__ == "__main__":
    app = build_app()
    print("✅ Бот запущен и слушает команды...")
    app.run_polling()
