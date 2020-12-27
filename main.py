from flask import Flask
import bot

app = Flask(__name__)

app.route("", methods=["GET"])
def welcome():
    bot.welcome()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
    print("API running")