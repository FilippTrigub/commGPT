import os

from dotenv import load_dotenv

from commGPT.FilePicker import FilePicker
from commGPT.TelegramMessageRetriever import retrieve_telegram_messages
from commGPT.chatminer.chatparsers import TelegramJsonParser

if __name__ == "__main__":
    load_dotenv()

    chat_name = 'Berlin helps Ukrainians'  # input('Enter the name of the chat: ')
    start_date = '22-04-2023'  # input('Enter the start date (dd-mm-yyyy): ')
    output_directory = 'telegram_messages'

    retrieve_telegram_messages(chat_name, start_date, output_directory)

    results = {}
    for file_path in os.listdir(output_directory):
        print(file_path)
        parser = TelegramJsonParser(os.path.join(output_directory, file_path), chat_name)
        parser.parse_file()
        results[file_path.split('.')[0]] = parser.parsed_messages

    print(results)
