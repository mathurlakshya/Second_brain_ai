import json
import os

SESSION_FILE = "session.json"


def save_session(user):

    with open(SESSION_FILE, "w") as f:
        json.dump(user, f)


def load_session():

    if not os.path.exists(SESSION_FILE):
        return None

    with open(SESSION_FILE) as f:
        return json.load(f)


def clear_session():

    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)