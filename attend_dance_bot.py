import logging
import json
from telegram.ext import Updater, CommandHandler

with open("config.json") as json_data_file:
    data = json.load(json_data_file)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

updater = Updater(token=data["bot"]["token"])


dispatcher = updater.dispatcher

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
            text="I\'m here to help manage your attendance")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
            text="Help guide")

def create_attendance(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id,
            text="Creating attendance")

def edit_attendance(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id,
            text="Editing attendance")
    
def end_attendance(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id,
            text="Deleting attendance")

start_handler = CommandHandler('start', start)
create_attendance_handler = CommandHandler('create_attendance', create_attendance)
edit_attendance_handler = CommandHandler('edit_attendance', edit_attendance)
end_attendance_handler = CommandHandler('end_attendance', end_attendance)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(create_attendance_handler)
dispatcher.add_handler(edit_attendance_handler)
dispatcher.add_handler(end_attendance_handler)

updater.start_polling()

