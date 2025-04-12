import os
import asyncio
import zipfile

from telegram import Update, InputMediaPhoto
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime



# 🔐 Укажи свой токен от BotFather
TOKEN = os.environ.get("BOT_TOKEN")
# 📁 Укажи базовую директорию, куда сохранять фото

###############BASE_DIR = "/Users/sib-coder/Documents/учеба/TGBOT/fotodir"
BASE_DIR = os.environ.get("BASE_DIR")

async def save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.today().strftime('%Y-%m-%d')
    folder = os.path.join(BASE_DIR, today)
    os.makedirs(folder, exist_ok=True)

    if update.message.photo:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_path = os.path.join(folder, f"{photo.file_id}.jpg")
        await file.download_to_drive(file_path)
        await update.message.reply_text("Фото сохранено 📸")
    else:
        await update.message.reply_text("Отправь мне фотографию!")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(BASE_DIR):
        await update.message.reply_text("Папок ещё нет 📁")
        return

    lines = []
    for folder in os.listdir(BASE_DIR):
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.isdir(folder_path):
            count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
            lines.append(f"📂 {folder}: {count} фото")

    message = "\n".join(lines) if lines else "Папок с фото пока нет."
    await update.message.reply_text(message)



async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❗ Укажи дату в формате: /get YYYY-MM-DD")
        return

    date_str = context.args[0]
    folder_path = os.path.join(BASE_DIR, date_str)

    if not os.path.exists(folder_path):
        await update.message.reply_text("❌ Папка с такой датой не найдена.")
        return

    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(".jpg")]

    if not files:
        await update.message.reply_text("😕 В папке нет фото.")
        return

    await update.message.chat.send_action(action=ChatAction.UPLOAD_PHOTO)

    # Разбиваем на пачки по 10 фото (Telegram ограничивает альбомы)
    chunk_size = 10
    for i in range(0, len(files), chunk_size):
        media_group = [InputMediaPhoto(open(photo, "rb")) for photo in files[i:i+chunk_size]]
        await update.message.reply_media_group(media=media_group)


async def zip_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❗ Укажи дату в формате: /zip YYYY-MM-DD")
        return

    date_str = context.args[0]
    folder_path = os.path.join(BASE_DIR, date_str)

    if not os.path.exists(folder_path):
        await update.message.reply_text("❌ Папка с такой датой не найдена.")
        return

    # Список всех файлов в папке
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(".jpg")]

    if not files:
        await update.message.reply_text("😕 В папке нет фото.")
        return

    # Создание архива
    zip_filename = f"{date_str}.zip"
    zip_filepath = os.path.join(BASE_DIR, zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))

    # Отправляем архив пользователю
    with open(zip_filepath, "rb") as zip_file:
        await update.message.reply_document(document=zip_file, filename=zip_filename)

    # Удаляем временный архив после отправки
    os.remove(zip_filepath)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    Привет! Я бот, который помогает работать с фото. Отправь мне фото и я положу его в папку сегодняшнего дня. 
    Вот список команд, которые ты можешь использовать:

    /info - Покажет список папок с фото и количество фото в каждой.
    
    /get <дата> - Отправит все фото из папки с указанной датой. Пример: /get 2025-04-08
    
    /zip <дата> - Сожмёт все фото из папки с указанной датой в архив и отправит его. Пример: /zip 2025-04-08
    
    /help - Покажет этот список команд.
    """
    await update.message.reply_text(help_text)

def main():
    print("✅ Бот запущен и готов принимать фото и команду /info")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("get", get_photo))
    app.add_handler(CommandHandler("zip", zip_and_send))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(MessageHandler(filters.PHOTO, save_photo))


    # 🚀 Стартуем (без asyncio.run)
    app.run_polling()

if __name__ == "__main__":
    main()
