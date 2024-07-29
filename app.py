import os

import requests
from flask import Flask, request, Response
import telegram
from telebot.credentials import bot_user_name, URL

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

global bot
global TOKEN

TOKEN = os.environ.get('TOKEN')
bot = telegram.Bot(token=TOKEN)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASSWORD')}@{os.environ.get('MYSQL_HOST')}:{os.environ.get('MYSQL_PORT')}/{os.environ.get('MYSQL_DATABASE')}"
# initialize the app with the extension
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chatId = db.Column(db.String(80), unique=True, nullable=False)
    businessCards = db.relationship('BusinessCard', backref='user', lazy=True)


class BusinessCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placeId = db.Column(db.String(80), unique=True, nullable=False)



@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/', methods=['POST'])
def post_example():
    if request.method == 'POST':
        # Access POST data from the request
        msg = request.get_json()
        print("Message: ", msg)

        # Trying to parse message
        try:
            print("There is a text")
            chat_id = msg['message']['chat']['id']
            text = msg['message']['text']  # This gets the text from the msg

            if not User.query.filter_by(chat_id=chat_id).first():
                new_user = User(chat_id=chat_id)
                db.session.add(new_user)
                db.session.commit()
                print("User saved to database")
            else:
                print("User already exists in the database")
      
            if text == "are you alive?":

                url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'  # Calling the telegram API to reply the message

                payload = {
                    'chat_id': chat_id,
                    'text': "yes, I am alive"
                }

                r = requests.post(url, json=payload)

                if r.status_code == 200:
                    return Response('ok', status=200)
                else:
                    return Response('Failed to send message to Telegram', status=500)
        except:
            print("No text found")

        return Response('ok', status=200)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(threaded=True, debug=True)
