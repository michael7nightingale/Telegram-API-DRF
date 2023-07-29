import json

import requests
from websockets.sync.client import connect


def get_token():
    user_data = {
        "phone_number": "+79999999999",
        "password": "password"
    }
    response = requests.post(
        url="http://localhost:8000/api/v1/auth/token/login/",
        json=user_data
    )
    token = response.json()['auth_token']
    return token


query_dict = {
    "token": get_token(),

}

query_string = "?" + "&".join(f"{k}={v}" for k, v in query_dict.items())
url = "ws://localhost:8000/chats/"

ws = connect(url + query_string)

ws.send(json.dumps({"action": "list", "request_id": "123019380192831903"}))
data = ws.recv()
print(data)


ws.send(json.dumps(
    {
        "action": "create",
        "request_id": "123019380192831903",
        "account_id": "2",
        "message": {
            "text": "Heelo, 2"
        }
    }
))
data = ws.recv()
print(data)
data = ws.recv()
print(data)
