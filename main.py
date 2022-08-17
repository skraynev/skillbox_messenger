from flask import Flask, request, render_template, escape, abort
from datetime import datetime
import json

from typing import Tuple

DB_FILE = 'db.json'

app = Flask(__name__)


def load_messages() -> list:
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
    return data['messages']


all_messages = load_messages()


def save_messages() -> None:
    data = {
        "messages": all_messages
    }
    with open(DB_FILE, 'w') as json_file:
        json.dump(data, json_file)


@app.route('/')
def index_page() -> str:
    return "Hello <b>Skillbox</b>!"


@app.route("/get_messages")
def get_messages() -> dict:
    return {"messages": all_messages}


@app.route('/chat')
def display_chat():
    return render_template('form.html')


# hmtl was updated to calculate and display this information
# on the /chat page
@app.route('/message_count')
def message_count() -> str:
    return str(len(all_messages))


def validate_length(field_name: str, value: str, min_val: int, max_val: int) -> None:
    if not value:
        raise ValueError(f"Field '{field_name}' is not specified in payload")
    else:
        current_len = len(value)
        if max_val < current_len or current_len < min_val:
            raise ValueError(
                f"Length of the field '{field_name}' does not match expected range "
                f"from {min_val} to {max_val}. The current length is {current_len}")


def input_data_validation(request_data: dict) -> Tuple[str, str]:
    sender = escape(request_data.get('name'))
    validate_length('name', sender, 3, 300)

    text = escape(request_data['text'])
    validate_length('text', text, 1, 3000)

    return sender, text

@app.route('/send_message')
def send_message() -> str:
    # should it be done with marshmallow lib?
    try:
        sender, text = input_data_validation(request.args)
    except ValueError as exc:
        abort(400)
    add_message(sender, text)
    save_messages()
    return 'OK'


def add_message(sender: str, text: str) -> None:
    new_message = {
        'sender': sender,
        'text': text,
        'time': datetime.now().time().isoformat(timespec='seconds'),
    }
    all_messages.append(new_message)


app.run()
