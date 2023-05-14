import asyncio
import os
import time

import streamlit as st
import requests
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from streamlit import session_state as ss


async def login_with_phone(container, phone_number):
    client = TelegramClient(f'./{phone_number}.session', int(os.getenv('TELEGRAM_API_ID')), os.getenv('TELEGRAM_API_HASH'))
    await client.connect()
    time.sleep(1)
    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        code = container.text_input("Enter the authentication code:")
        submit_code = container.button("Submit Authentication Code")
        time.sleep(5)
        while not await client.is_user_authorized() and (not submit_code or not code):
            time.sleep(1)
        if submit_code and code:
            try:
                await client.sign_in(phone_number, code)
                return True
            except SessionPasswordNeededError:
                return False
    return True


def login_window(container):
    phone_number = container.text_input("Enter your phone number:", key='phone_number')
    submit_phone = container.button("Submit Phone Number", key='submit_phone')

    if submit_phone:
        if phone_number:
            asyncio.set_event_loop(asyncio.new_event_loop())
            result = asyncio.run(login_with_phone(container, phone_number))
            if result:
                ss.logged_in = True
            container.success("Logged in successfully!")
        else:
            container.error("Please enter a phone number.")


def main():
    st.title("CommGPT")
    login_state = st.empty()
    container = login_state.container()

    login_window(container)

    if 'logged_in' in ss.keys() and ss.logged_in:
        login_state.empty()
        st.sidebar.header("Enter chat information")
        phone_number = st.sidebar.text_input("Phone Number:", "")
        chat_name = st.sidebar.text_input("Chat Name:", "")
        chat_link = st.sidebar.text_input("Chat Link:", "")
        start_date = st.sidebar.text_input("Start Date (dd-mm-YYYY):", "08-05-2023")

        chat_history = st.empty()
        chat_input = st.text_input("You:", key='input_main_screen')

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
