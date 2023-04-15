import os
from typing import Optional
import requests
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, Request
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from fastapi import FastAPI

line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handle = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/callback")
async def callback(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        handle.handle(body.decode(), signature)
    except InvalidSignatureError:
        return {"error": "Invalid signature"}

    return {"message": "OK"}


@handle.add(MessageEvent, message=TextMessage)
def handle_message(event):
    reply = generate_reply(event.message.text, os.environ['OPENAI_API_KEY'])
    ans = (reply['choices'][0]['message']['content'])

    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=ans)
    )


class Body(BaseModel):
    content: Optional[str] = None


def generate_reply(user_message, api_key):
    chatgpt_url = "https://api.openai.com/v1/chat/completions"

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-4',
        'messages': [
            {
                'role': 'user',
                'content': user_message
            }
        ],
        'temperature': 0.5,
    }

    try:
        response = requests.post(chatgpt_url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    else:
        return response.json()


# ローカルで開発サーバーを起動するためのコード
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
