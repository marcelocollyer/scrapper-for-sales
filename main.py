
import logging
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import magalu
import natura
import amazon
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():

    folder_path = os.getcwd().replace("\\", "\\\\")
    print("OKOKOKOK", folder_path)

    application = ApplicationBuilder().token('6481858651:AAGY3oOoJ7XO3iMAPIrEPe5MTQlYw8VYWq4').build()
    
    application.add_handler(CommandHandler('mag', magalu.handler))
    application.add_handler(CommandHandler('nat', natura.handler))
    application.add_handler(CommandHandler('ama', amazon.handler))
    
    application.run_polling()



main()
