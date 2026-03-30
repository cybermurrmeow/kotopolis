from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'alinakuznecova63802@gmail.com'
app.config['MAIL_PASSWORD'] = 'ojfz yahm gprn fwwl'
app.config['MAIL_DEFAULT_SENDER'] = 'alinakuznecova63802@gmail.com'

mail = Mail(app)

with app.app_context():
    try:
        msg = Message("Тестовое письмо", recipients=["alinakuznecova63802@gmail.com"])
        msg.body = "Это тестовое письмо из Котополиса"
        mail.send(msg)
        print("✅ Тестовое письмо отправлено!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")