import asyncio
import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
import telethon
from telethon.tl.functions.messages import GetHistoryRequest
from telethon import TelegramClient


async def get_telegram_chat(client, chat_name=None, chat_link=None):
    """
    Gets the specified chat. If chat_link is specified, it will be used to get the chat. Otherwise, the chat_name will.
    Args:
        client: The TelegramClient object.
        chat_name: The name of the chat to get.
        chat_link: The link to the chat to get.

    Returns: The chat object.
    """
    if chat_link:
        chat = await client.get_entity(chat_link)
    else:
        # Find the specified chat
        chats = await client.get_dialogs()
        chat = None
        for c in chats:
            if c.title == chat_name:
                chat = c.entity
    return chat


async def get_messages(client, chat_name=None, chat_link=None, start_date=datetime.today().strftime('%d-%m-%Y')):
    """
    Gets all of the messages from the specified chat since the specified date. Returns a list of dictionaries with the
    following keys: 'text', 'date', 'sender_id'.
    param client: The TelegramClient object.
    param chat_name: The name of the chat to get the messages from.
    param chat_link: The link to the chat to get the messages from.
    param start_date: The date to start getting messages from.

    return: A list of dictionaries with the following keys: 'text', 'date', 'sender_id'.
    """
    chat = await get_telegram_chat(client, chat_name, chat_link)

    # Get all of the messages since the specified date
    messages = []
    date = datetime.strptime(start_date, '%d-%m-%Y')
    while date <= datetime.now():
        print(f'Getting messages from {date.strftime("%d-%m-%Y")}.')
        get_history = await client(
            GetHistoryRequest(peer=chat, offset_id=0, offset_date=datetime.now(), add_offset=0, limit=1000,
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


async def telegram_messages(phone_number, api_id, api_hash, chat_name=None, chat_link=None,
                            start_date=datetime.today().strftime('%d-%m-%Y')):
    client = TelegramClient(f'./{phone_number}.session', api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        try:
            await client.sign_in(phone_number, code=input('Enter the code sent to your Telegram: '))
        except telethon.errors.rpc_error_list.PhoneCodeInvalidError:
            return None

    chat_messages = await get_messages(client=client, chat_name=chat_name, chat_link=chat_link, start_date=start_date)

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


async def main(phone_number, output_directory, chat_name=None, chat_link=None,
               start_date=datetime.today().strftime('%d-%m-%Y')):
    load_dotenv()
    # phone_number = os.getenv('PHONE_NUMBER') todo
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    chat_messages = await telegram_messages(
        phone_number=phone_number,
        api_id=api_id,
        api_hash=api_hash,
        chat_name=chat_name,
        chat_link=chat_link,
        start_date=start_date
    )
    write_to_file(output_directory, chat_messages, chat_name)


def retrieve_telegram_messages(phone_number, chat_name, chat_link, start_date, output_directory):
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # todo database is locked after first execution: fix this
    asyncio.run(main(phone_number=phone_number,
                     output_directory=output_directory,
                     chat_name=chat_name,
                     chat_link=chat_link,
                     start_date=start_date))

    # loop.run_until_complete(main(output_directory=output_directory,
    #                              chat_name=chat_name,
    #                              chat_link=chat_link,
    #                              start_date=start_date))
