import os

import yaml
from dotenv import load_dotenv
from haystack import Document
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import OpenAIAnswerGenerator, EmbeddingRetriever
from haystack.pipelines import GenerativeQAPipeline
from haystack.utils import print_answers

from commGPT.TelegramMessageRetriever import retrieve_telegram_messages
from commGPT.chatminer.chatparsers import TelegramJsonParser


class TelegramGPT:
    def __init__(self, chat_name, chat_link, start_date, output_directory):
        self.generator = None
        self.retriever = None
        self.document_store = None
        self.pipeline = None
        self.chat_name = chat_name
        self.chat_link = chat_link
        self.start_date = start_date
        self.output_directory = output_directory

    def download_telegram_messages(self, remove_old_files=True):
        """
        Downloads all the messages from the chat_name chat since the start_date and stores them in the output_directory.
        Returns: True if at least one file was downloaded, False otherwise.
        """
        if remove_old_files:
            for file_path in os.listdir(self.output_directory):
                os.remove(os.path.join(self.output_directory, file_path))

        initial_number_of_files = len(os.listdir(self.output_directory))
        retrieve_telegram_messages(self.chat_name, self.chat_link, self.start_date, self.output_directory)

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

