# Chatbot en Telegram

Scource code for a Rasa chatbot integrated with telegram.
The bot is currently located in the url: https://t.me/AsistenteCompraBot but you migth create a new one with @botFather and update the credentials file.


## ⚙️ Installation & Setup

To install it you just need to run the following command in an environment with Python
3.10 or higher with [poetry](https://python-poetry.org/docs/#installation) installed:

`poetry install`

Additionally to integrate the bot with telegram you will need to install [ngrok](https://ngrok.com/) or a similar API gateway provider.


## 💻 Usage

- Run training model: `rasa train`
- Run the actions server: `rasa run actions`
- Run Ngrok in standar rasa server `ngrok http 5005 --region eu`
- Update the `credentials.yml` file before next step.
- Run the server: `rasa run --enable-api`