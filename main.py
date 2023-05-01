import asyncio
import configparser
import os
from datetime import datetime

from telethon import TelegramClient
from telethon.tl.types import PeerChannel
from loguru import logger

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read('setting/config.ini')
config.read('setting_user/config.ini')

channel_url = str(config['link_to_the_group']['target_group_entity'])
api_id = int(config['telegram_settings']['id'])
api_hash = config['telegram_settings']['hash']

# Логирование программы
logger.add("setting/log/log.log", rotation="1 MB", compression="zip")


async def download_images_from_telegram_channel(channel_url: str, api_id: int, api_hash: str) -> None:
    """
    Функция скачивает все изображения из заданного канала Telegram
    :param channel_url: ссылка на канал Telegram, например "https://t.me/+VrDS1_bG0bExNzQy"
    :param api_id: ID программы
    :param api_hash: HASH программы
    """
    # Устанавливаем соединение с аккаунтом Telegram
    client = TelegramClient('accounts/telethon', api_id, api_hash)
    await client.connect()

    # Получаем объект канала
    channel = await client.get_entity(channel_url)

    # Получаем ID чата или группы
    peer_channel = PeerChannel(channel.id)

    # Перебираем посты
    async for message in client.iter_messages(peer_channel):
        # Если в посте есть медиафайлы
        if message.media is not None:
            print(f"Downloading media from post {message.id}")

            # Определяем дату и время публикации поста
            post_date = datetime.fromtimestamp(message.date.timestamp()).strftime('%Y-%m-%d_%H-%M')

            # Создаем папку с датой и временем поста, если ее еще нет
            folder_path = f"download/{post_date}"
            os.makedirs(folder_path, exist_ok=True)

            # Имя файла включает идентификатор поста и идентификатор фотографии
            file_path = f"{folder_path}/{message.id}.jpg"

            # Скачиваем медиафайл
            await message.download_media(file_path)

            print(f"Downloaded media to {file_path}")

    # Закрываем соединение
    await client.disconnect()

if __name__ == "__main__":
    try:
        # Выполняем парсинг
        asyncio.run(download_images_from_telegram_channel(channel_url, api_id, api_hash))
    except Exception as e:
        logger.exception(e)
        print("[bold red][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
