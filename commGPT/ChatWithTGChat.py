import os

from dotenv import load_dotenv
from haystack.utils import print_answers

from commGPT.src.TelegramGPT import TelegramGPT

if __name__ == "__main__":
    load_dotenv()

    chat_name = "Berlin helps Ukrainians"  # input('Enter the name of the chat: ')
    chat_link = 'https://t.me/Norman_Storman'
    start_date = '22-04-2023'  # input('Enter the start date (dd-mm-yyyy): ')

    query = 'What is best way to explore the island?'  # input('Enter your question: ')

    tgpt = TelegramGPT(chat_name=chat_name, chat_link=chat_link, start_date=start_date,
                       output_directory=os.getenv('OUTPUT_DIRECTORY'))
    # tgpt.download_telegram_messages()
    tgpt.parse_telegram_messages()

    tgpt.set_pipeline()
    tgpt.write_messages_to_document_store()

    prompt_query = f"Synthesize a comprehensive answer from the following text for the given question. " \
                   f"Provide a clear and concise response that summarizes the key points and information presented " \
                   f"in the text. " \
                   f"Your answer should be in your own words and be no longer than 50 words. " \
                   f"If an answer cannot be found in the supplied related documents, respond with" \
                   f"'I cannot find a suitable answer in the supplied chats, sorry.'" \
                   f"\n\n Question: {query} " \
                   f"\n\n Answer: "
    prediction = tgpt.pipeline.run(query=prompt_query)

    print_answers(prediction, details="minimum")
