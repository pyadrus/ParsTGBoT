import configparser
import getpass
import os
import sqlite3

from rich import print
from rich.console import Console
from telethon import TelegramClient
from telethon.errors import *

console = Console()

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read('setting/config.ini')

channel_url = str(config['link_to_the_group']['target_group_entity'])
api_id = int(config['telegram_settings']['id'])
api_hash = config['telegram_settings']['hash']


async def writing_link_to_the_group() -> configparser.ConfigParser:
    """Записываем ссылку для parsing групп / каналов"""
    target_group_entity_user = console.input("[bold green][+] Введите ссылку на группу : ")  # Вводим ссылку на группу
    # Находим ссылку в файле и меняем на свою
    config.get('link_to_the_group', 'target_group_entity')
    config.set('link_to_the_group', 'target_group_entity', target_group_entity_user)
    return config


async def writing_api_id_api_hash() -> configparser.ConfigParser:
    """Записываем api, hash полученный с помощью регистрации приложения на сайте https://my.telegram.org/auth"""
    api_id_data = console.input("[bold green][+] Введите api_id : ")
    config.get('telegram_settings', 'id')
    config.set('telegram_settings', 'id', api_id_data)
    api_hash_data = console.input("[bold green][+] Введите api_hash : ")
    config.get('telegram_settings', 'hash')
    config.set('telegram_settings', 'hash', api_hash_data)
    return config


async def writing_settings_to_a_file(config):
    """Запись данных в файл setting/config.ini"""
    with open('setting/config.ini', 'w') as setup:
        config.write(setup)


def reading_the_id_and_hash():
    """Считываем id и hash"""
    config.read('setting/config.ini')  # Файл с настройками
    api_id_data = config['telegram_settings']['id']  # api_id с файла setting_user/api_id_api_hash.ini
    api_hash_data = config['telegram_settings']['hash']  # api_hash с файла setting_user/api_id_api_hash.ini
    return api_id_data, api_hash_data


def connecting_to_the_database():
    """Подключение к базе данных"""
    with sqlite3.connect('setting/software_database.db') as sqlite_connection:
        cursor = sqlite_connection.cursor()
        """
        cursor — это объект в памяти компьютера с методами для проведения SQL команд, хранения итогов их 
        выполнения (например части таблицы или (view)) и методов доступа к ним.
        """
        return sqlite_connection, cursor


def writing_data_to_the_db(creating_a_table, writing_data_to_a_table, entities) -> None:
    """Запись действий аккаунта в базу данных"""
    sqlite_connection, cursor = connecting_to_the_database()
    cursor.execute("DELETE FROM config")  # Удаление всех строк из таблицы config
    cursor.execute(creating_a_table)  # Считываем таблицу
    try:
        cursor.executemany(writing_data_to_a_table, (entities,))
    finally:  # Выполняется в любом случае, было исключение или нет
        sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
        cursor.close()  # cursor_members.close() – закрытие соединения с БД.


async def telegram_connect(phone, api_id, api_hash) -> TelegramClient:
    """Account telegram connect, с проверкой на валидность, если ранее не было соединения, то запрашиваем код"""
    client = TelegramClient(f"accounts/{phone}", api_id, api_hash)
    await client.connect()  # Подсоединяемся к Telegram
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            # Если ранее аккаунт не подсоединялся, то просим ввести код подтверждения
            await client.sign_in(phone, code=console.input("[bold red][+] Введите код: "))
        except SessionPasswordNeededError:
            """
            https://telethonn.readthedocs.io/en/latest/extra/basic/creating-a-client.html#two-factor-authorization-2fa
            """
            # Если аккаунт имеет password, то просим пользователя ввести пароль
            await client.sign_in(password=getpass.getpass())
        except ApiIdInvalidError:
            print("[bold red][!] Не валидные api_id/api_hash")
    return client


async def connecting_new_account() -> None:
    """Вводим данные в базу данных setting/software_database.db"""
    api_id_data, api_hash_data = reading_the_id_and_hash()
    phone_data = console.input("[bold green][+] Введите номер телефона : ")  # Вводим номер телефона
    entities = (api_id_data, api_hash_data, phone_data)
    creating_a_table = "CREATE TABLE IF NOT EXISTS config(id, hash, phone)"
    writing_data_to_a_table = "INSERT INTO config (id, hash, phone) VALUES (?, ?, ?)"
    writing_data_to_the_db(creating_a_table, writing_data_to_a_table, entities)
    # Подключение к Telegram, возвращаем client для дальнейшего отключения сессии
    client = await telegram_connect(phone_data, api_id_data, api_hash_data)
    client.disconnect()  # Разрываем соединение telegram


def delete_row_db(table, column, value) -> None:
    """Удаляет строку из таблицы"""
    sqlite_connection, cursor = connecting_to_the_database()
    cursor.execute(f"SELECT * from {table}")  # Считываем таблицу
    cursor.execute(f"DELETE from {table} where {column} = ?", (value,))  # Удаляем строку
    sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
    cursor.close()  # cursor_members.close() – закрытие соединения с БД.


def telegram_phone_number_banned_error(client, phone):
    """Аккаунт banned, удаляем banned аккаунт"""
    client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
    delete_row_db(table="config", column="phone", value=phone)
    try:
        os.remove(f"accounts/{phone}.session")  # Находим и удаляем сессию
    except FileNotFoundError:
        print(f"[green]Файл {phone}.session был ранее удален")  # Если номер не найден, то выводим сообщение


def get_from_the_list_phone_api_id_api_hash(row):
    """Получаем со списка phone, api_id, api_hash"""
    users = {'id': int(row[0]), 'hash': row[1], 'phone': row[2]}
    # Вытягиваем данные из кортежа, для подстановки в функцию
    phone = users['phone']
    api_id = users['id']
    api_hash = users['hash']
    return phone, api_id, api_hash


def open_the_db_and_read_the_data(name_database_table) -> list:
    """Открываем базу считываем данные в качестве аргумента передаем имя таблицы"""
    sqlite_connection, cursor = connecting_to_the_database()
    cursor.execute(f"SELECT * from {name_database_table}")
    records: list = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()  # Закрываем базу данных
    return records


async def checking_accounts():
    """Проверка аккаунтов"""
    error_sessions = []  # Создаем словарь, для удаления битых файлов session
    print("[bold red] Проверка аккаунтов!")
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    for row in records:
        # Получаем со списка phone, api_id, api_hash
        phone_old, api_id, api_hash = get_from_the_list_phone_api_id_api_hash(row)
        try:
            client = TelegramClient(f"accounts/{phone_old}", api_id, api_hash)
            try:
                await client.connect()  # Подсоединяемся к Telegram
                # Если аккаунт не авторизирован, то удаляем сессию
                if not await client.is_user_authorized():
                    telegram_phone_number_banned_error(client, phone_old)  # Удаляем номер телефона с базы данных
            except AuthKeyDuplicatedError:
                # На данный момент аккаунт запущен под другим ip
                print(f"На данный момент аккаунт {phone_old} запущен под другим ip")
                # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                await client.disconnect()
                try:
                    os.replace(f"accounts/{phone_old}.session", f"accounts/invalid_account/{phone_old}.session")
                except FileNotFoundError:
                    # Если в папке accounts нет папки invalid_account, то создаем папку invalid_account
                    print("В папке accounts нет папки invalid_account, создаем папку invalid_account")
                    # Создаем папку invalid_account в папке accounts
                    os.makedirs("accounts/invalid_account")
                    os.replace(f"accounts/{phone_old}.session", f"accounts/invalid_account/{phone_old}.session")
            except (PhoneNumberBannedError, UserDeactivatedBanError):
                # Удаляем номер телефона с базы данных
                telegram_phone_number_banned_error(client, phone_old)  # Удаляем номер телефона с базы данных
            await client.disconnect()
        except sqlite3.DatabaseError:
            # session файл не является базой данных
            print(f"Битый файл {phone_old}.session")
            # Удаляем не валидную сессию
            error_sessions.append([phone_old])
    return error_sessions
