def form_message_with_options(msg_object):
    text_to_send=(
            f"*{msg_object['index']}. {msg_object['event_detail']}*"
            f"\n\n"
        )
    for option in msg_object["options"]:
        text_to_send += f"*{option['name']}*:\n\n\n"

    return text_to_send
