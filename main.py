# -*- coding: utf-8 -*-
import asyncio
import os
from datetime import datetime

from loguru import logger
from rich import print
from telethon import TelegramClient
from telethon.tl.types import PeerChannel

from system.system_setting import api_hash, connecting_new_account, checking_accounts
from system.system_setting import api_id
from system.system_setting import channel_url
from system.system_setting import console
from system.system_setting import writing_api_id_api_hash
from system.system_setting import writing_link_to_the_group
from system.system_setting import writing_settings_to_a_file

# Логирование программы
logger.add("setting/log/log.log", rotation="1 MB", compression="zip")


def find_file_in_folder(folder_path, file_extension):
    """
    Функция принимает путь к папке и расширение файла.
    Возвращает имя файла с заданным расширением, найденного в папке.
    Если такого файла нет, возвращает None.
    :param folder_path: путь к папке
    :param file_extension: расширение файла
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith(file_extension):
            return file_name
    return None


async def connecting_to_an_account(api_id: int, api_hash: str):
    """
    Устанавливает соединение с учетной записью Telegram.
    :param api_id: id аккаунта Telegram
    :param api_hash: хэш аккаунта Telegram
    """
    folder_path = 'accounts'
    file_extension = '.session'
    file_name = find_file_in_folder(folder_path, file_extension)
    if file_name:
        print(f'Найден аккаунт {file_name}')
        # Устанавливаем соединение с аккаунтом Telegram
        client = TelegramClient(f'accounts/{file_name}', api_id, api_hash)
        await client.connect()
        return client
    else:
        print('Аккаунт не найден')


async def download_images_from_telegram_channel(channel_url: str, ) -> None:
    """
    Функция скачивает все изображения из заданного канала Telegram
    :param channel_url: ссылка на канал Telegram, например "https://t.me/+VrDS1_bG0bExNzQy"
    """

    client = await connecting_to_an_account(api_id, api_hash)

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


async def main():
    """Основное окно программы"""
    await checking_accounts()
    try:
        console.print("[bold green][1] - Подключение нового аккаунта")
        console.print("[bold green][2] - Запуск parsing")
        console.print("[bold green][3] - Настройки")
        user_input = console.input("[bold red][+] Введите номер : ")  # Вводим номер
        if user_input == "1":
            """Подключение нового аккаунта"""
            await connecting_new_account()
        elif user_input == "2":
            """Запуск parsing"""
            await download_images_from_telegram_channel(channel_url)
        elif user_input == "3":
            """Настройки"""
            console.print("[bold green][1] - Запись api_id и api_hash")
            console.print("[bold green][2] - Запись ссылки, для дальнейшего parsing")
            user_input = console.input("[bold red][+] Введите номер : ")  # Вводим номер
            if user_input == "1":
                """Запись api_id и api_hash"""
                print("[bold red][!] Получить api_id, api_hash можно на сайте https://my.telegram.org/auth")
                await writing_settings_to_a_file(config=await writing_api_id_api_hash())
                await main()  # После не правильного ввода номера возвращаемся в начальное меню
            elif user_input == "2":
                """Запись ссылки, для дальнейшего parsing"""
                console.print(f"[bold green][!] Давайте запишем ссылку для parsing, ссылка должна быть [bold red]одна!")
                await writing_settings_to_a_file(config=await writing_link_to_the_group())
                await main()  # После не правильного ввода номера возвращаемся в начальное меню
            else:
                await main()  # После не правильного ввода номера возвращаемся в начальное меню
        else:
            await main()  # После не правильного ввода номера возвращаемся в начальное меню
    except KeyboardInterrupt:
        """Закрытие окна программы"""
        print("[!] Скрипт остановлен!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(e)
        print("[bold red][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
