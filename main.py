import os
from telegram.ext import ApplicationBuilder, CommandHandler
from flask import Flask, jsonify
import threading
from telegram.ext import ApplicationBuilder, CommandHandler
import magalu
import natura
import amazon
import mercado_livre
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP"}), 200

def start_flask():
    app.run(host='0.0.0.0', port=8080, use_reloader=False)

def main():
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    application = ApplicationBuilder().token(bot_token).build()

    # Configurar os comandos do bot
    application.add_handler(CommandHandler('mag', magalu.handler))
    application.add_handler(CommandHandler('nat', natura.handler))
    application.add_handler(CommandHandler('ama', amazon.handler))
    application.add_handler(CommandHandler('ml', mercado_livre.handler))

    # Iniciar Flask em uma thread separada
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    # Iniciar o bot na thread principal
    application.run_polling()

if __name__ == '__main__':
    main()
