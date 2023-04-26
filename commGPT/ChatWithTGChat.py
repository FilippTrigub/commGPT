from dotenv import load_dotenv

from commGPT.FilePicker import FilePicker
from commGPT.TelegramMessageRetriever import retrieve_telegram_messages
from commGPT.chatminer.chatparsers import TelegramJsonParser

if __name__ == "__main__":
    load_dotenv()

    chat_name = 'Berlin helps Ukrainians'  # input('Enter the name of the chat: ')
    start_date = '22-04-2023'  # input('Enter the start date (dd-mm-yyyy): ')

    # file_picker = FilePicker('telegram_messages')
    # file_picker.watch_continuous()

    retrieve_telegram_messages(chat_name, start_date)

    # TelegramJsonParser = TelegramJsonParser(file_picker.PICKED_FILE_PATH, chat_name)
    # results = TelegramJsonParser.parse_file()

    # print(results)
