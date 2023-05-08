import os
import threading

from haystack import Document
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import OpenAIAnswerGenerator, EmbeddingRetriever
from haystack.pipelines import GenerativeQAPipeline

from api.src.TelegramMessageRetriever import retrieve_telegram_messages
from api.src.chatparsers import TelegramJsonParser


class TelegramGPT:
    def __init__(self, output_directory):
        self.phone_number = None
        self.start_date = None
        self.chat_link = None
        self.chat_name = None
        self.generator = None
        self.retriever = None
        self.document_store = None
        self.pipeline = None
        self.output_directory = output_directory

    def set_params(self, phone_number, chat_name, chat_link, start_date):
        self.phone_number = phone_number
        self.chat_name = chat_name
        self.chat_link = chat_link
        self.start_date = start_date

    def download_telegram_messages(self, remove_old_files=True):
        """
        Downloads all the messages from the chat_name chat since the start_date and stores them in the output_directory.
        Returns: True if at least one file was downloaded, False otherwise.
        """
        if remove_old_files:
            for file_path in os.listdir(self.output_directory):
                os.remove(os.path.join(self.output_directory, file_path))

        initial_number_of_files = len(os.listdir(self.output_directory))

        t = threading.Thread(target=retrieve_telegram_messages,
                             args=(
                             self.phone_number, self.chat_name, self.chat_link, self.start_date, self.output_directory))
        t.start()
        t.join()
        # retrieve_telegram_messages(self.chat_name, self.chat_link, self.start_date, self.output_directory)

        print(f'Downloaded {len(os.listdir(self.output_directory)) - initial_number_of_files} files.')

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

        print(f'Parsed {len(self.results)} files.')

    def set_pipeline(self):

        if os.path.exists(os.getenv('FAISS_INDEX_PATH')) and os.path.exists(os.getenv('FAISS_CONFIG_PATH')):
            self.document_store = FAISSDocumentStore.load(index_path=os.getenv('FAISS_INDEX_PATH'),
                                                          config_path=os.getenv('FAISS_CONFIG_PATH'))
        else:
            self.document_store = FAISSDocumentStore(
                sql_url=os.getenv('FAISS_SQL_URL'),
                faiss_index_factory_str="Flat",
                embedding_dim=768,
                return_embedding=False,
                similarity="dot_product"
            )
        self.retriever = EmbeddingRetriever(embedding_model='sentence-transformers/all-mpnet-base-v2',
                                            document_store=self.document_store,
                                            api_key=os.getenv('OPENAI_API_KEY'))
        self.generator = OpenAIAnswerGenerator(
            api_key=os.getenv('OPENAI_API_KEY'),
            api_version="2022-12-01",
            model="text-davinci-003",
            max_tokens=50,
            presence_penalty=0.1,
            frequency_penalty=0.1,
            top_k=5,
            temperature=0.5
        )
        self.pipeline = GenerativeQAPipeline(generator=self.generator,
                                             retriever=self.retriever)

        print('Pipeline set.')

    def write_messages_to_document_store(self):
        for file_path, messages in self.results.items():
            documents = []
            for index, row in messages.get_df().iterrows():
                meta = {key: str(row[key]) for key in row.keys() if key != 'message'}
                documents.append(Document(content=row['message'], meta=meta))
            self.document_store.write_documents(documents)
        self.document_store.update_embeddings(self.retriever)
        self.document_store.save(index_path=os.getenv('FAISS_INDEX_PATH'), config_path=os.getenv('FAISS_CONFIG_PATH'))
        print('Messages written to document store.')
        # todo rewrite to load from dict
