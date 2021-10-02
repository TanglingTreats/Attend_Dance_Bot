from uuid import uuid4
from telegram import (
        InlineQueryResultArticle,
        InputTextMessageContent,
        ParseMode
    )

def form_message_with_options(msg_object):
    text_to_send=(
            f"*{msg_object['event_detail']}*"
            f"\n\n"
        )
    for option in msg_object["options"]:
        text_to_send += f"*{option['name']}*:\n\n\n"

    return text_to_send

def get_query_article(msg_object, query):
    article = InlineQueryResultArticle(
            id = str(uuid4()),
            title=msg_object[query]['event_detail'],
            input_message_content=InputTextMessageContent(
                form_message_with_options(msg_object[query]),
                parse_mode=ParseMode.MARKDOWN
            )
        )
    return article

def get_all_articles(msg_object):
    query_articles = []
    for msg in msg_object:
        article = InlineQueryResultArticle(
                id = str(uuid4()),
                title=msg['event_detail'],
                input_message_content=InputTextMessageContent(
                    form_message_with_options(msg),
                    parse_mode=ParseMode.MARKDOWN
                )
            )
        query_articles.append(article)
    return query_articles

def get_message_index(command):
    return command.split(" ")[1]

