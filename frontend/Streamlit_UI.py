import asyncio
import os

import streamlit as st
import requests
from dotenv import load_dotenv
from telethon import TelegramClient


def main():
    st.title("CommGPT")

    st.sidebar.title("Input Fields")
    st.sidebar.header("Enter chat information")
    phone_number = st.sidebar.text_input("Phone Number:", "")
    chat_name = st.sidebar.text_input("Chat Name:", "")
    chat_link = st.sidebar.text_input("Chat Link:", "")
    start_date = st.sidebar.text_input("Start Date (dd-mm-YYYY):", "")

    st.title("Chat Window")
    chat_history = st.empty()
    chat_input = st.text_input("You:")

    retrieval_done = False
    if st.sidebar.button("Submit"):
        payload = {
            "phone_number": phone_number,
            "chat_name": chat_name,
            "chat_link": chat_link,
            "start_date": start_date
        }
        retrieval_done = requests.post(f"http://localhost:{os.getenv('API_PORT')}/retrieve_messages", json=payload)

    if st.button('Send', key='send_button', disabled=not retrieval_done):
        # display user input in chat history
        chat_history.write(f"You: {chat_input}")

        response = requests.post(f"http://localhost:{os.getenv('API_PORT')}/query", json={"query": chat_input})
        bot_response = response.json()

        # display bot response in chat history
        chat_history.write(f"Bot: {bot_response['answer']}")


if __name__ == "__main__":
    load_dotenv()
    main()
