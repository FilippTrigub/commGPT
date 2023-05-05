import os
import asyncio
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

import commGPT.src.TelegramMessageRetriever as tmr


class TestTelegramMethods(unittest.TestCase):
    def setUp(self):
        self.phone_number = "1234567890"
        self.api_id = 12345
        self.api_hash = "abcdef123456"
        self.chat_name = "test_chat"
        self.chat_link = "https://t.me/test_chat"
        self.start_date = "2023-01-01"
        self.output_directory = "test_output"

    @patch("telethon.TelegramClient.get_dialogs")
    @patch("telethon.TelegramClient.get_entity")
    async def test_get_telegram_chat(self, mock_get_entity, mock_get_dialogs):
        client = MagicMock(TelegramClient)

        # Test with chat_link
        chat = await tmr.get_telegram_chat(client, chat_name=self.chat_name, chat_link=self.chat_link)
        mock_get_entity.assert_called_with(self.chat_link)

        # Test with chat_name
        mock_chat = MagicMock()
        mock_chat.title = self.chat_name
        mock_get_dialogs.return_value = [mock_chat]

        chat = await tmr.get_telegram_chat(client, chat_name=self.chat_name)
        mock_get_dialogs.assert_called()

    @patch("commGPT.src.TelegramMessageRetriever.get_telegram_chat")
    async def test_get_messages(self, mock_get_telegram_chat):
        client = MagicMock(TelegramClient)
        mock_chat = MagicMock()
        mock_get_telegram_chat.return_value = mock_chat

        with patch.object(TelegramClient, "__call__") as mock_call:
            mock_history = MagicMock()
            mock_message = MagicMock()
            mock_message.date.strftime.return_value = "2023-01-01 12:00:00"
            mock_message.message = "Test message"
            mock_message.from_id.user_id = 123
            mock_history.messages = [mock_message]
            mock_call.return_value = mock_history

            messages = await tmr.get_messages(client, chat_name=self.chat_name, start_date=self.start_date)

            mock_call.assert_called_with(GetHistoryRequest(peer=mock_chat, offset_id=0, offset_date=datetime.now(),
                                                           add_offset=0, limit=1000, max_id=0, min_id=0, hash=0))

            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]["text"], "Test message")
            self.assertEqual(messages[0]["date"], "2023-01-01 12:00:00")
            self.assertEqual(messages[0]["sender_id"], 123)

    @patch("commGPT.src.TelegramMessageRetriever.get_messages")
    async def test_telegram_messages(self, mock_get_messages):
        with patch("telethon.TelegramClient.connect") as mock_connect, \
                patch("telethon.TelegramClient.is_user_authorized") as mock_is_user_authorized, \
                patch("telethon.TelegramClient.send_code_request") as mock_send_code_request, \
                patch("telethon.TelegramClient.sign_in") as mock_sign_in:

            mock_connect.return_value = None
            mock_is_user_authorized.return_value = True
            mock_send_code_request.return_value = None
            mock_sign_in.return_value = None

            client = MagicMock(TelegramClient)

            messages = await tmr.telegram_messages(
                phone_number=self.phone_number,
                api_id=self.api_id,
                api_hash=self.api_hash,
                chat_name=self.chat_name,
                chat_link=self.chat_link,
                start_date=self.start_date
            )

            mock_get_messages.assert_called_with(client=client, chat_name=self.chat_name, chat_link=self.chat_link, start_date=self.start_date)
    def test_write_to_file(self):
        output_path = "test_output"
        messages = [{"text": "Test message", "date": "2023-01-01 12:00:00", "sender_id": 123}]
        chat_name = "test_chat"

        with patch("builtins.open", unittest.mock.mock_open()) as mock_open, \
                patch("json.dump") as mock_dump:
            tmr.write_to_file(output_path, messages, chat_name)

            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            file_pattern = os.path.join(output_path, f"{timestamp}_test_chat.json")
            mock_open.assert_called_with(file_pattern, "w")
            mock_dump.assert_called_with(messages, mock_open.return_value)

    @patch("commGPT.src.TelegramMessageRetriever.main")
    def test_retrieve_telegram_messages(self, mock_main):
        loop = asyncio.get_event_loop()
        tmr.retrieve_telegram_messages(chat_name=self.chat_name, chat_link=self.chat_link, start_date=self.start_date, output_directory=self.output_directory)

        mock_main.assert_called_with(output_directory=self.output_directory,
                                     chat_name=self.chat_name,
                                     chat_link=self.chat_link,
                                     start_date=self.start_date)

