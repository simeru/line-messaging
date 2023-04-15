import os
import requests
from typing import Optional
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, Request
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn
)
from fastapi import FastAPI
from googlesearch import search
from google_images_search import GoogleImagesSearch

line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handle = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


class Body(BaseModel):
    content: Optional[str] = None


@app.get("/image")
async def image():
    return get_image_urls()


def get_image_urls(query='cute kittens'):
    gis = GoogleImagesSearch(
        os.environ["GOOGLE_API_KEY"], os.environ["SEARCH_ENGINE_ID"])
    search_params = {
        "q": query,
        "num": 5,
        "imgSize": "large",
    }

    gis.search(search_params)
    image_urls = [image.url for image in gis.results()]
    if image_urls.count == 0:
        image_urls = ["http://abehiroshi.la.coocan.jp/abe-top-20190328-2.jpg"]

    return image_urls


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
    ans = ''
    if event.message.text[-2:] in '画像':
        return send_image_message(event)

    reply = generate_reply(event.message.text, os.environ['OPENAI_API_KEY'])
    ans = (reply['choices'][0]['message']['content'])
    print('human: ' + event.message.text)
    print('bot: ' + ans)
    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=ans)
    )


def send_image_message(event):
    query = event.message.text[:-2]
    try:
        image_urls = get_image_urls(query)
        carousel_columns = [
            CarouselColumn(
                thumbnail_image_url=url,
                text=query,
                actions=[
                    {
                        "type": "uri",
                        "label": "View",
                        "uri": url
                    }
                ]
            )
            for url in image_urls
        ]
        carousel_template_message = TemplateSendMessage(
            alt_text=query,
            template=CarouselTemplate(columns=carousel_columns)
        )
        line_bot_api.reply_message(
            event.reply_token, carousel_template_message)
        # image_messages = [ImageSendMessage(
        #     original_content_url=url, preview_image_url=url) for url in image_urls]
        # line_bot_api.reply_message(event.reply_token, image_messages)
    except LineBotApiError as e:
        print("Error:", e)


def generate_reply(user_message, api_key):
    chatgpt_url = "https://api.openai.com/v1/chat/completions"

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
