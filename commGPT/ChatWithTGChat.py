import os

import uvicorn as uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_socketio import SocketManager
from haystack.utils import print_answers
from pydantic import BaseModel

from commGPT.src.TelegramGPT import TelegramGPT

app = FastAPI()
socket_manager = SocketManager(app=app)

load_dotenv()
tgpt = TelegramGPT(output_directory=os.getenv('OUTPUT_DIRECTORY'))


class ChatInfo(BaseModel):
    chat_name: str
    chat_link: str
    start_date: str


@app.post("/retrieve_messages")
async def retrieve_messages(chat_info: ChatInfo):
    """
    Retrieve messages from Telegram chat and save them to a file.
    """
    tgpt.set_params(chat_name=chat_info.chat_name, chat_link=chat_info.chat_link, start_date=chat_info.start_date)

    tgpt.download_telegram_messages()
    tgpt.parse_telegram_messages()

    tgpt.set_pipeline()
    tgpt.write_messages_to_document_store()

    return True


class Query(BaseModel):
    query: str


@app.post("/query")
async def query(query: Query):
    """
    Query the model.
    """
    no_result_statement = "I cannot find a suitable answer in the supplied chats, sorry."
    prompt_query = f"Synthesize a comprehensive answer from the following text for the given question. " \
                   f"Provide a clear and concise response that summarizes the key points and information presented " \
                   f"in the text. " \
                   f"Your answer should be in your own words and be no longer than 50 words. " \
                   f"If an answer cannot be found in the supplied related documents, respond with" \
                   f"'{no_result_statement}'" \
                   f"\n\n Question: {query.query} " \
                   f"\n\n Answer: "
    prediction = tgpt.pipeline.run(query=prompt_query)
    # print_answers(prediction, details="minimum") #todo log this

    for answer in prediction["answers"]:
        if answer.answer != no_result_statement:
            return answer

    return prediction["answers"][0]


@socket_manager.on("connect")
async def on_connect(sid: str):
    print(f"Client {sid} connected")


@socket_manager.on("disconnect")
async def on_disconnect(sid: str):
    print(f"Client {sid} disconnected")


if __name__ == "__main__":

    uvicorn.run("ChatWithTGChat:app", host="0.0.0.0", port=8090, log_level="info", reload=True)
