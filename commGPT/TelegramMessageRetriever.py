import asyncio
import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from telethon.tl.functions.messages import GetHistoryRequest
import telethon
from telethon import TelegramClient


async def get_messages(client, chat_name, start_date):
    # Find the specified chat
    chats = await client.get_dialogs()
    chat = None
    for c in chats:
        if c.title == chat_name:
            chat = c
            break
    if chat is None:
        return None

    # Get all of the messages since the specified date
    messages = []
    date = datetime.strptime(start_date, '%d-%m-%Y')
    while date <= datetime.now():
        print(f'Getting messages from {date.strftime("%d-%m-%Y")}.')
        get_history = await client(
            GetHistoryRequest(peer=chat.entity, offset_id=0, offset_date=datetime.now(), add_offset=0, limit=1000,
                              max_id=0, min_id=0, hash=0))
        if not get_history.messages:
            break
        print(f'Found {len(get_history.messages)} messages.')
        for msg in get_history.messages:
            print('Looking at message from ' + msg.date.strftime('%d-%m-%Y %H:%M:%S'))
            if msg.date >= date.astimezone():
                message = {
                    'text': msg.message,
                    'date': msg.date.strftime('%d-%m-%Y %H:%M:%S'),
                    'sender_id': msg.from_id.user_id
                }
                messages.append(message)
        print(f'Found {len(messages)} messages since {start_date}.')
        date = date + timedelta(days=1)

    return messages


async def telegram_messages(phone_number, api_id, api_hash, chat_name, start_date):
    client = TelegramClient(phone_number, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        try:
            await client.sign_in(phone_number, code=input('Enter the code sent to your Telegram: '))
        except telethon.errors.rpc_error_list.PhoneCodeInvalidError:
            return None

    chat_messages = await get_messages(client, chat_name, start_date)

    if not chat_messages:
        return None

    return chat_messages


def write_to_file(output_path, messages, chat_name):
    print('Writing messages to file...')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    if messages is None:
        return None
    file_path = os.path.join(output_path, f'{timestamp}_{chat_name}.json')
    with open(file_path, 'w') as f:
        json.dump(messages, f)


async def main(chat_name, start_date):
    load_dotenv()
    phone_number = os.getenv('PHONE_NUMBER')  # input('Enter your phone number: ')
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    # chat_name = 'Berlin helps Ukrainians'  # input('Enter the name of the chat: ')
    # start_date = '22-04-2023'  # input('Enter the start date (dd-mm-yyyy): ')
    chat_messages = await telegram_messages(
        phone_number=phone_number,
        api_id=api_id,
        api_hash=api_hash,
        chat_name=chat_name,
        start_date=start_date
    )
    write_to_file('telegram_messages', chat_messages, chat_name)


def retrieve_telegram_messages(chat_name, start_date):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(chat_name, start_date))

# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
