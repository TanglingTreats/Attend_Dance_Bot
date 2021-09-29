import logging
import json
from datetime import datetime
from telegram import (
        Update, 
        ReplyKeyboardMarkup, 
        InlineKeyboardMarkup, 
        InlineKeyboardButton
    )
from telegram.ext import (
        Updater,
        CommandHandler,
        ConversationHandler,
        MessageHandler,
        Filters,
        CallbackContext,
        CallbackQueryHandler
    )

with open("config.json") as json_data_file:
    data = json.load(json_data_file)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

keeb_options = [['Yes', 'No']]
markup_keeb = ReplyKeyboardMarkup(keeb_options, one_time_keyboard=True)

buttons = [[
        InlineKeyboardButton(text=keeb_options[0][0], callback_data='y'),
        InlineKeyboardButton(text=keeb_options[0][1], callback_data='n')
    ]]
inline_keeb = InlineKeyboardMarkup(buttons)

messages = []

option = {}
options = []
current_msg = {}

ENTER_DATE, ENTER_EVENT, ENTER_OPTIONS, REQUIRE_REASON = range(4)

END = ConversationHandler.END

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
    prompt = "To start, what's the event about?"
    update.message.reply_text(text=prompt)

    return ENTER_EVENT

def retrieve_event_date(update: Update, context: CallbackContext):
    text = update.message.text
    reply = f'Creating an event on {text}'
    update.message.reply_text(reply)

    date_obj = datetime.strptime(text, "%d %b %Y")
    print(date_obj)
    current_msg['date'] = text

    message = "Next, what's the event about?"
    context.bot.send_message(chat_id=update.effective_chat.id,
            text=message)
    
    return ENTER_EVENT

def retrieve_event_detail(update: Update, context: CallbackContext):
    text = update.message.text
    reply = f'Event is about: {text}'
    update.message.reply_text(reply)
    
    current_msg['event_detail'] = text

    message = "Next, what's are your options for this attendance list?"
    context.bot.send_message(chat_id=update.effective_chat.id,
            text=message)

    return ENTER_OPTIONS

def retrieve_event_options(update: Update, context: CallbackContext):
    global option
    option = {}
    text = update.message.text
    reply = f'\'{text}\' has been entered'
    update.message.reply_text(reply)

    option["name"] = text

    message = "Does this option require attendees \
to supply additional information?"

    update.message.reply_text(message, reply_markup=inline_keeb)

    return REQUIRE_REASON

def retrieve_option_reason(update: Update, context: CallbackContext):
    text = update.callback_query.data

    option["require_reason"] = text

    options.append(option)

    message = "Continue typing your options, if not, type \"Done\""
    context.bot.send_message(chat_id=update.effective_chat.id,
            text=message)

    return ENTER_OPTIONS

def edit_attendance(update: Update, context: CallbackContext):
   context.bot.send_message(chat_id=update.effective_chat.id,
            text="Editing attendance. This is still a WIP!")
    
def end_attendance(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
            text="Deleting attendance. This is still a WIP!")

def done(update: Update, context: CallbackContext):
    current_msg["options"] = options

    print(current_msg)

    context.bot.send_message(chat_id=update.effective_chat.id,
            text="You are done creating the attendance")
    return END

def regular_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data['choice'] = text
    reply = f'{text}'
    update.message.reply_text(reply)

    return ENTER_EVENT

def main():
    updater = Updater(token=data["bot"]["token"])

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help_command)
    create_attendance_handler = CommandHandler('create_attendance',
            create_attendance)
    edit_attendance_handler = CommandHandler('edit_attendance',
            edit_attendance)
    end_attendance_handler = CommandHandler('end_attendance',
            end_attendance)

    conv_handler = ConversationHandler(
        entry_points=[create_attendance_handler],
        states = {
            ENTER_DATE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), retrieve_event_date
                    )
                ],
            ENTER_EVENT: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), retrieve_event_detail
                    )
                ],
            ENTER_OPTIONS: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), retrieve_event_options
                    )
                ],
            REQUIRE_REASON: [
                CallbackQueryHandler(
                    retrieve_option_reason,
                    pattern=f'^y$|^n$')
                ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )


    # Command Handlers
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(edit_attendance_handler)
    dispatcher.add_handler(end_attendance_handler)

    # Conversation Handlers
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

if __name__ == "__main__":
    main()
