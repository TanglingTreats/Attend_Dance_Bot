import re
import logging
import json
from message_util import (
        form_message_with_options,
        get_message_index,
        get_query_article,
        get_all_articles
        )
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
        CallbackQueryHandler,
        InlineQueryHandler
    )

with open("config.json") as json_data_file:
    data = json.load(json_data_file)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

keeb_options = [['Yes', 'No']]

# Yes No buttons
yn_buttons = [[
    InlineKeyboardButton(text=keeb_options[0][0], callback_data='y'),
    InlineKeyboardButton(text=keeb_options[0][1], callback_data='n')
]]
yn_inline_keeb = InlineKeyboardMarkup(yn_buttons)


messages = []

option = {}
options = []

current_msg = {}

ENTER_EVENT, ENTER_OPTIONS, REQUIRE_REASON = range(3)

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

def retrieve_event_detail(update: Update, context: CallbackContext):
    text = update.message.text
    reply = f'Event is about: {text}'
    update.message.reply_text(reply)
    
    msgs_len = len(messages)
    current_msg['index'] = msgs_len
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

    update.message.reply_text(message, reply_markup=yn_inline_keeb)

    return REQUIRE_REASON

def retrieve_option_reason(update: Update, context: CallbackContext):
    global options

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
            parse_mode="Markdown",
            text="Deleting attendance. This is still a *WIP*!")

def done(update: Update, context: CallbackContext):
    current_msg["options"] = options

    text_to_send = form_message_with_options(current_msg)

    messages.append(current_msg)

    pub_msg_buttons = [[
        InlineKeyboardButton(text="Publish",
            switch_inline_query=f"pub {current_msg['index']}"),
    ]]
    pub_msg_keeb = InlineKeyboardMarkup(pub_msg_buttons)

    context.bot.send_message(chat_id=update.effective_chat.id,
            text="You are done creating the attendance")

    context.bot.send_message(chat_id=update.effective_chat.id,
            parse_mode="Markdown",
            text=text_to_send,
            reply_markup=pub_msg_keeb)

    clear_global_variables()
    return END

def select_message_to_publish(update: Update, context: CallbackContext):
    query = update.inline_query.query

    results = []

    if query == "" or re.match(r"^pub$", query):
        results = get_all_articles(messages)
    elif re.match(r"^pub [0-9]+$", query):
        msg_index = int(get_message_index(query))
        results = [get_query_article(messages, msg_index)]

    update.inline_query.answer(results)

def publish_message(update: Update, context: CallbackContext):
    pub_option = get_message_index(update.callback_query.data)

def clear_global_variables():
    global current_msg
    global options

    current_msg={}
    options=[]
    
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

    select_msg_handler = InlineQueryHandler(select_message_to_publish)

    conv_handler = ConversationHandler(
        entry_points=[create_attendance_handler],
        states = {
            ENTER_EVENT: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^[Dd]one$')), retrieve_event_detail
                    )
                ],
            ENTER_OPTIONS: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^[Dd]one$')), retrieve_event_options
                    )
                ],
            REQUIRE_REASON: [
                CallbackQueryHandler(
                    retrieve_option_reason,
                    pattern=f'^y$|^n$')
                ],
        },
        fallbacks=[MessageHandler(Filters.regex('^[Dd]one$'), done)],
    )


    # Command Handlers
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(edit_attendance_handler)
    dispatcher.add_handler(end_attendance_handler)

    # Inline Handlers
    dispatcher.add_handler(select_msg_handler)

    # Conversation Handlers
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

if __name__ == "__main__":
    main()
