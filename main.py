
import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler
import magalu
import natura
import amazon

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():

    bot_token = os.environ['TELEGRAM_BOT_TOKEN']

    application = ApplicationBuilder().token(bot_token).build()
    
    application.add_handler(CommandHandler('mag', magalu.handler))
    application.add_handler(CommandHandler('nat', natura.handler))
    application.add_handler(CommandHandler('ama', amazon.handler))
    
    application.run_polling()

main()
