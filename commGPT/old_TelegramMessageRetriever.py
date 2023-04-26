# Set up and authentication
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime, timedelta
import json


# class TelegramMessageRetriever:
#
#     def __init__(self):
#         self.client = None
#         load_dotenv()
#         self.api_id = int(os.getenv('TELEGRAM_API_ID'))
#         self.api_hash = os.getenv('TELEGRAM_API_HASH')
#         self.client = self.authenticate()
#
#     def authenticate(self):
#         client = TelegramClient('session_name', self.api_id, self.api_hash)
#         client.connect()
#         if not client.is_user_authorized():
#             try:
#                 client.send_code_request(input('Enter your phone number: '))
#                 client.sign_in(code=input('Enter the code sent to your Telegram: '))
#             except SessionPasswordNeededError:
#                 client.sign_in(password=input('Enter your second factor password: '))
#         return client
#
#     def get_messages(self, chat_name, start_date):
#         print('Getting messages...')
#         # Find the specified chat
#         chats = self.client.get_dialogs()
#         chat = None
#         for c in chats:
#             if c.title == chat_name:
#                 chat = c
#                 break
#         if not chat:
#             return None
#
#         # Get all of the messages since the specified date
#         messages = []
#         date = datetime.strptime(start_date, '%d-%m-%Y')
#         while date <= datetime.now():
#             print(f'Getting messages from {date.strftime("%d-%m-%Y")}.')
#             get_history = self.client(
#                 GetHistoryRequest(peer=chat.entity, offset_id=0, offset_date=datetime.now(), add_offset=0, limit=1000,
#                                   max_id=0, min_id=0, hash=0))
#             if not get_history.messages:
#                 break
#             print(f'Found {len(get_history.messages)} messages.')
#             for msg in get_history.messages:
#                 print('Looking at message from ' + msg.date.strftime('%d-%m-%Y %H:%M:%S'))
#                 if msg.date >= date.astimezone():
#                     message = {
#                         'text': msg.message,
#                         'date': msg.date.strftime('%d-%m-%Y %H:%M:%S'),
#                         'sender_id': msg.from_id.user_id
#                     }
#                     messages.append(message)
#             print(f'Found {len(messages)} messages since {start_date}.')
#             date = date + timedelta(days=1)
#
#         return messages
#
#     @staticmethod
#     def write_to_file(output_path, messages, chat_name):
#         print('Writing messages to file...')
#         if messages is None:
#             return None
#         file_path = os.path.join(output_path, f'{chat_name}.json')
#         with open(file_path, 'w') as f:
#             json.dump(messages, f)
#         return file_path


def authenticate():
    client = TelegramClient('session_name', api_id, api_hash)
    client.connect()
    if not client.is_user_authorized():
        try:
            client.send_code_request(input('Enter your phone number: '))
            client.sign_in(code=input('Enter the code sent to your Telegram: '))
        except SessionPasswordNeededError:
            client.sign_in(password=input('Enter your second factor password: '))
    return client


# async def get_messages(session_name, api_id, api_hash, chat_name, start_date):
#     async with TelegramClient(session_name, api_id, api_hash) as client:
#         print('Getting messages...')
#         # Find the specified chat
#         chats = client.get_dialogs()
#         chat = None
#         for c in chats:
#             if c.title == chat_name:
#                 chat = c
#                 break
#         if not chat:
#             return None
#
#         # Get all of the messages since the specified date
#         messages = []
#         date = datetime.strptime(start_date, '%d-%m-%Y')
#         while date <= datetime.now():
#             print(f'Getting messages from {date.strftime("%d-%m-%Y")}.')
#             get_history = client(
#                 GetHistoryRequest(peer=chat.entity, offset_id=0, offset_date=datetime.now(), add_offset=0, limit=1000,
#                                   max_id=0, min_id=0, hash=0))
#             if not get_history.messages:
#                 break
#             print(f'Found {len(get_history.messages)} messages.')
#             for msg in get_history.messages:
#                 print('Looking at message from ' + msg.date.strftime('%d-%m-%Y %H:%M:%S'))
#                 if msg.date >= date.astimezone():
#                     message = {
#                         'text': msg.message,
#                         'date': msg.date.strftime('%d-%m-%Y %H:%M:%S'),
#                         'sender_id': msg.from_id.user_id
#                     }
#                     messages.append(message)
#             print(f'Found {len(messages)} messages since {start_date}.')
#             date = date + timedelta(days=1)
#
#     return messages



async def get_messages(session_name, api_id, api_hash, chat_name, start_date, output_path):
    async with TelegramClient(session_name, api_id, api_hash) as client:
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
            get_history = client(
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

        write_to_file(output_path, messages, chat_name)
        return messages

def write_to_file(output_path, messages, chat_name):
    print('Writing messages to file...')
    if messages is None:
        return None
    file_path = os.path.join(output_path, f'{chat_name}.json')
    with open(file_path, 'w') as f:
        json.dump(messages, f)
    return file_path


if __name__ == '__main__':
    load_dotenv()
    session_name = "read_messages"
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')

    chat_name = 'Berlin helps Ukrainians'  # input('Enter the name of the chat: ')
    start_date = '22-04-2023'  # input('Enter the start date (dd-mm-yyyy): ')
    messages = get_messages(session_name, api_id, api_hash, chat_name, start_date, 'telegram_messages')
    # write_to_file('telegram_messages', messages, chat_name)

# if __name__ == '__main__':
#     load_dotenv()
#
#     chat_name = 'Berlin helps Ukrainians'  # input('Enter the name of the chat: ')
#     start_date = '22-04-2023'  # input('Enter the start date (dd-mm-yyyy): ')
#
#     TGRetriever = TelegramMessageRetriever()
#     TGRetriever.write_to_file('telegram_messages', TGRetriever.get_messages(chat_name, start_date), chat_name)
