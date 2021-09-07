import json
from collections import defaultdict

from app.metrics import save_users_metrics


class UserStates:
    init = 0
    saved_last_name_ru = 1
    confirmed = 10


class User:
    def __init__(self, last_name_ru=None, last_name_en=None):
        self.state = UserStates.init
        self.subscribed = True
        self.last_name_ru = last_name_ru
        self.last_name_en = last_name_en

    def to_dict(self):
        return {
            "state": self.state,
            "subscribed": self.subscribed,
            "last_name_ru": self.last_name_ru,
            "last_name_en": self.last_name_en,
        }

    def from_dict(self, data):
        self.state = data["state"]
        self.subscribed = data["subscribed"]
        self.last_name_ru = data["last_name_ru"]
        self.last_name_en = data["last_name_en"]


def read_file():
    try:
        with open("users.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    result = defaultdict(User)
    for user_id in data:
        user = User()
        user.from_dict(data[user_id])
        result[int(user_id)] = user

    save_users_metrics(result)

    return result


def save_file():
    data = {str(user_id): user.to_dict() for user_id, user in users.items()}
    with open("users.json", "w") as f:
        json.dump(data, f)

    save_users_metrics(users)


users = read_file()
