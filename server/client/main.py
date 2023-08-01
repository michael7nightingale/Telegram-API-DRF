from websockets.sync.client import connect
import requests
import json


def get_token():
    user_data = {
        "phone_number": "89937740834",
        "password": "password"
    }
    response = requests.post(
        url="http://localhost:8000/api/v1/auth/token/login/",
        json=user_data
    )
    print(123, response.content)
    token = response.json()['auth_token']
    return token


query_dict = {
    "token": get_token(),

}

query_string = "?" + "&".join(f"{k}={v}" for k, v in query_dict.items())
url = "ws://localhost:8000/chat/"

ws = connect(url + query_string)


def get_chat_list():
    data = {"action": "chat_list", "request_id": "123019380192831903"}
    ws.send(json.dumps(data))
    data = ws.recv()
    print(data)


def create_chat():
    data = {
        "action": "chat_create",
        "request_id": "123019380192831903",
        "account_id": "1",
        "message": {
            "text": "I am programming this",
            "medias": [
                {
                    "media": open("manage.py").read()
                }
            ],
            "type": "chat"
        },
    }
    ws.send(json.dumps(data))
    data = ws.recv()
    print(data)


def send_chat_message():
    data = {
        "action": "message_send",
        "request_id": "123019380192831903",
        "text": "I am 123 this",
        "medias": [
            {
                "media": open("manage.py").read()
            }
        ],
        "type": "chat",
        "content_object": "1"
    }
    ws.send(json.dumps(data))
    data = ws.recv()
    print(data)


def create_group():
    data = {
        "action": "group_create",
        "request_id": "123019380192831903",
        "title": "Programming",
        "accounts": [
            {"account_id": "1"}
        ],
    }
    ws.send(json.dumps(data))
    data = ws.recv()
    print(data)


def update_message():
    data = {
        "action": "message_update",
        "request_id": "123019380112392831903",
        "text": "Updated one",
        "id": "1"
    }
    ws.send(json.dumps(data))
    data = ws.recv()
    print(data)


def update_group():
    data = {
        "action": "group_update",
        "request_id": "123019380112392831903",
        "title": "Updated tiotle c #",
        "id": "1"
    }
    ws.send(json.dumps(data))
    data = ws.recv()
    print(data)


if __name__ == "__main__":
    # create_group()
    get_chat_list()
    pass
