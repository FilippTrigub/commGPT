import os

from dotenv import load_dotenv
from haystack import Document
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import OpenAIAnswerGenerator, EmbeddingRetriever
from haystack.pipelines import GenerativeQAPipeline

from commGPT.TelegramMessageRetriever import retrieve_telegram_messages
from commGPT.chatminer.chatparsers import TelegramJsonParser


class TelegramGPT:
    def __init__(self, chat_name, start_date, output_directory):
        self.chat_name = chat_name
        self.start_date = start_date
        self.output_directory = output_directory

    def download_telegram_messages(self):
        """
        Downloads all the messages from the chat_name chat since the start_date and stores them in the output_directory.
        Returns: True if at least one file was downloaded, False otherwise.
        """
        initial_number_of_files = len(os.listdir(self.output_directory))
        retrieve_telegram_messages(self.chat_name, self.start_date, self.output_directory)
        return len(os.listdir(self.output_directory)) - initial_number_of_files > 0

    def parse_telegram_messages(self):
        """
        Parses all the files in the output directory and stores the results in a dictionary.
        Returns: True if at least one file was parsed, False otherwise.
        """
        self.results = {}
        for file_path in os.listdir(self.output_directory):
            parser = TelegramJsonParser(os.path.join(self.output_directory, file_path), self.chat_name)
            parser.parse_file()
            self.results[file_path.split('.')[0]] = parser.parsed_messages

        return len(self.results) > 0

    def set_pipeline(self):
        self.generator = OpenAIAnswerGenerator(
            api_key=os.getenv('OPENAI_API_KEY'),
            api_version="2022-12-01",
            model="text-davinci-003",
            max_tokens=50,
            presence_penalty=0.1,
            frequency_penalty=0.1,
            top_k=3,
            temperature=0.5
        )
        self.document_store = FAISSDocumentStore(
            faiss_index_factory_str="Flat",
            return_embedding=False,
            similarity="dot_product"
        )
        self.document_store.save(index_path="data/test_index.faiss", config_path="data/test_config.json")
        self.retriever = EmbeddingRetriever(embedding_model='ada', document_store=self.document_store)
        self.pipeline = GenerativeQAPipeline(generator=self.generator, retriever=self.retriever)

    def write_messages_to_document_store(self):
        for file_path, messages in self.results.items():
            documents = []
            for index, row in messages.get_df().iterrows():
                meta = {key: str(row[key]) for key in row.keys() if key != 'message'}
                documents.append(Document(content=row['message'], meta=meta))
            self.document_store.write_documents(documents)
        #todo rewrite to load from dict

if __name__ == "__main__":
    load_dotenv()

    chat_name = 'Berlin helps Ukrainians'  # input('Enter the name of the chat: ')
    start_date = '22-04-2023'  # input('Enter the start date (dd-mm-yyyy): ')
    output_directory = 'telegram_messages'

    tgpt = TelegramGPT(chat_name, start_date, output_directory)
    # status = tgpt.download_telegram_messages()
    # print(f"Downloaded at least one file: {status}")
    status = tgpt.parse_telegram_messages()
    print(f"Parsed at least one file: {status}")

    tgpt.set_pipeline()
    tgpt.write_messages_to_document_store()
