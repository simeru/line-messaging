from flask import Flask
from flask_line_bot import app  # flask_line_bot は、Flaskアプリケーションが定義されているファイル名です
from hypercorn.config import Config
from hypercorn.asyncio import serve as hypercorn_serve

if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:8000"]  # 任意のポート番号を設定
    hypercorn_serve(app, config)
