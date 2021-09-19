import logging
import json
from telegram import Update
from telegram.ext import (
        Updater,
        CommandHandler,
        ConversationHandler,
        MessageHandler,
        Filters,
        CallbackContext
    )

with open("config.json") as json_data_file:
    data = json.load(json_data_file)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

def start(update: Update, context: CallbackContext):
    message = "I\'m here to help manage your attendance"
    context.bot.send_message(chat_id=update.effective_chat.id, 
            text=message)

def help_command(update: Update, context: CallbackContext):
    message="Thanks for using the bot!\n\n\
Use /create_attendance to start your attendance list!"

    context.bot.send_message(chat_id=update.effective_chat.id,
            text=message)

def create_attendance(update: Update, context: CallbackContext):
    prompt = "To start, please tell me the date of the event"
    update.message.reply_text(text=prompt)

    return TYPING_CHOICE

def edit_attendance(update: Update, context: CallbackContext):
   context.bot.send_message(chat_id=update.effective_chat.id,
            text="Editing attendance")
    
def end_attendance(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
            text="Deleting attendance")

def regular_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data['choice'] = text
    reply = f'{text} is that correct?'
    update.message.reply_text(reply)

    return TYPING_REPLY

def main():
    updater = Updater(token=data["bot"]["token"])

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help_command)
    create_attendance_handler = CommandHandler('create_attendance', create_attendance)
    edit_attendance_handler = CommandHandler('edit_attendance', edit_attendance)
    end_attendance_handler = CommandHandler('end_attendance', end_attendance)

    conv_handler = ConversationHandler(
        entry_points=[create_attendance_handler],
        states = {
            CHOOSING: [],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice
                )
               ],
            TYPING_REPLY: [],
        },
        fallbacks=[],
    )


    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(conv_handler)
    #dispatcher.add_handler(create_attendance_handler)
    dispatcher.add_handler(edit_attendance_handler)
    dispatcher.add_handler(end_attendance_handler)

    updater.start_polling()

if __name__ == "__main__":
    main()
