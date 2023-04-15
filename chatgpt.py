import requests
import os


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
    user_message = "子供が歯磨きをしてくれない"
    reply = generate_reply(user_message, os.environ['OPENAI_API_KEY'])
    print(reply['choices'][0]['message']['content'])
