import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv

from commGPT.chatminer.chatparsers import ParsedMessageCollection, ParsedMessage
from commGPT.src.TelegramGPT import TelegramGPT


class TestTelegramGPT(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.chat_name = "test_chat"
        self.chat_link = "https://t.me/test_chat"
        self.start_date = "2023-01-01"
        self.output_directory = "test_output"

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        self.telegram_gpt = TelegramGPT(
            chat_name=self.chat_name,
            chat_link=self.chat_link,
            start_date=self.start_date,
            output_directory=self.output_directory,
        )

    def tearDown(self):
        if os.path.exists(self.output_directory):
            for file_path in os.listdir(self.output_directory):
                os.remove(os.path.join(self.output_directory, file_path))
            os.rmdir(self.output_directory)

    def test_download_telegram_messages(self):
        with patch("commGPT.src.TelegramGPT.retrieve_telegram_messages") as mock_retrieve_telegram_messages:
            result = self.telegram_gpt.download_telegram_messages()
            mock_retrieve_telegram_messages.assert_called_with(
                self.chat_name, self.chat_link, self.start_date, self.output_directory
            )

    def test_parse_telegram_messages(self):
        with patch("commGPT.src.TelegramGPT.TelegramJsonParser") as mock_telegram_json_parser:
            mock_parser_instance = MagicMock()
            mock_parser_instance.parsed_messages = [{"text": "test_message"}]
            mock_telegram_json_parser.return_value = mock_parser_instance

            with open(os.path.join(self.output_directory, "test_file.json"), "w") as test_file:
                test_file.write('{"test": "data"}')

            self.telegram_gpt.parse_telegram_messages()

            self.assertTrue("test_file" in self.telegram_gpt.results)
            self.assertEqual(len(self.telegram_gpt.results["test_file"]), 1)
            self.assertEqual(self.telegram_gpt.results["test_file"][0], {"text": "test_message"})

    def test_set_pipeline(self):
        with patch("commGPT.src.TelegramGPT.FAISSDocumentStore") as mock_faiss_document_store, \
                patch("commGPT.src.TelegramGPT.EmbeddingRetriever") as mock_embedding_retriever, \
                patch("commGPT.src.TelegramGPT.OpenAIAnswerGenerator") as mock_openai_answer_generator, \
                patch("commGPT.src.TelegramGPT.GenerativeQAPipeline") as mock_generative_qa_pipeline:

            self.telegram_gpt.set_pipeline()

            mock_faiss_document_store.assert_called()
            mock_embedding_retriever.assert_called()
            mock_openai_answer_generator.assert_called()
            mock_generative_qa_pipeline.assert_called()

    def test_write_messages_to_document_store(self):
        with patch("commGPT.src.TelegramGPT.Document") as mock_document:
            test_collection = ParsedMessageCollection()
            test_collection.append(ParsedMessage(message='test_message', timestamp=datetime.now(), author='test_author'))
            self.telegram_gpt.results = {
                "test_collection": test_collection
            }
            self.telegram_gpt.document_store = MagicMock()

            self.telegram_gpt.write_messages_to_document_store()

            mock_document.assert_called()
            self.telegram_gpt.document_store.write_documents.assert_called()
            self.telegram_gpt.document_store.update_embeddings.assert_called()
            self.telegram_gpt.document_store.save.assert_called()

