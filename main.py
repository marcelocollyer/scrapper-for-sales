
import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler
import magalu
import natura
import amazon
import mercado_livre

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

def main():

    bot_token = '6976550644:AAFtPc1sp_qoQcZqIOdQpysqzFrXW_HyiEc'

    application = ApplicationBuilder().token(bot_token).build()
    
    application.add_handler(CommandHandler('mag', magalu.handler))
    application.add_handler(CommandHandler('nat', natura.handler))
    application.add_handler(CommandHandler('ama', amazon.handler))
    application.add_handler(CommandHandler('ml', mercado_livre.handler))
    
    application.run_polling()

main()
