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
    # businessCards = db.relationship('BusinessCard', backref='user', lazy=True)


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
        print("db is ", db)

        # Trying to parse message
        try:
            print("There is a text")
            chat_id = msg['message']['chat']['id']
            text = msg['message']['text']  # This gets the text from the msg

            url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'  # Calling the telegram API to reply the message

            payload = {
                'chat_id': chat_id,
                'text': "you said: " + text
            }

            r = requests.post(url, json=payload)
            
            if not User.query.filter_by(chatId=chat_id).first():
                new_user = User(chatId=chat_id)
                db.session.add(new_user)
                db.session.commit()
                print("User saved to database")
                return Response('User saved to database', status=200)
            else:
                print("User already exists in the database")
                return Response('User already exists in the database', status=200)
            
        except Exception as e:
            print("No text found")
            print("exception ", e)

        return Response('ok', status=200)


if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database created")
        except Exception as e:
            print("Error creating database: ", e)
    app.run(threaded=True)
