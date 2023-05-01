import asyncio
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import PeerChannel


async def main():
    # Группа или канал с которого парсим
    chat = "https://t.me/+VrDS1_bG0bExNzQy"
    # ID программы
    api_id = 7655060
    # HASH программы
    api_hash = 'cc1290cd733c1f1d407598e5a31be4a8'
    # Соединяемся с аккаунтом Telegram
    client = TelegramClient('accounts/telethon', api_id, api_hash)
    # Запускаем соединение
    await client.connect()
    channel = await client.get_entity(chat)
    # Получаем ID чата или группы
    c = await client.get_entity(PeerChannel(channel.id))
    # Перебираем посты
    async for m in client.iter_messages(c):
        if m.media is not None:
            print(m.media)
            # Скачиваем изображение
            post_date = datetime.fromtimestamp(m.date.timestamp()).strftime(' _%Y-%m-%d_%H-%M')
            folder_path = f"image/{post_date}"
            os.makedirs(folder_path, exist_ok=True)  # Создаем папку с датой и временем поста, если ее еще нет
            file_path = f"{folder_path}/{m.id}.jpg"  # Имя файла включает идентификатор поста и идентификатор фотографии
            await m.download_media(file_path)
            print(f"Downloaded media to {file_path}")
    # Закрываем соединение
    await client.disconnect()


asyncio.run(main())


