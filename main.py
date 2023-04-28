import os
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterPhotos

# Введите свои данные API Telegram
api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'
phone = 'YOUR_PHONE_NUMBER'

# Инициализация клиента Telethon
client = TelegramClient('session_name', api_id, api_hash)


async def main():
    # Авторизация в Telegram
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        await client.sign_in(phone, input('Введите код: '))

    # ID группы или канала, который нужно спарсить
    group_id = YOUR_GROUP_ID

    # Получение всех фотографий из постов
    messages = await client.get_messages(group_id, filter=InputMessagesFilterPhotos)

    # Создание папки для сохранения фотографий, если она не существует
    if not os.path.exists('photos'):
        os.makedirs('photos')

    # Сохранение фотографий в папки, имена которых соответствуют ID постов
    for message in messages:
        folder_name = f'photos/{message.id}'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        for i, photo in enumerate(message.photo):
            file_name = f'{folder_name}/{i}.jpg'
            await client.download_media(photo, file=file_name)

    print('Фотографии сохранены в папках постов.')


# Запуск скрипта
with client:
    client.loop.run_until_complete(main())
