from pyrogram import Client


def connecting_to_an_account():
    """Подключение к аккаунту"""
    api_id = 12345
    api_hash = "0123456789abcdef0123456789abcdef"
    app = Client("accounts/telethon", api_id=api_id, api_hash=api_hash)
    app.start()
    return app


def getting_the_account_name_and_number(app):
    """Получение имени и номера аккаунта"""
    # Get the phone number and username of the current account
    me = app.get_me()
    phone_number = me.phone_number or "not available"
    username = me.username or "not available"
    print("Phone number:", phone_number)
    print("Username:", username)


def main():
    app = connecting_to_an_account()
    getting_the_account_name_and_number(app)
    app.stop()


if __name__ == "__main__":
    main()
