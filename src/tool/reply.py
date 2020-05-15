import os
from urllib.parse import urlencode

from src.tool import message, filter
from src.context import Context


def introduction(userId):
    persona_id = filter.get_persona_id()
    return message.push_text(
        id=userId, text=Context.introduction, persona=persona_id)


def pairing(userId):
    persona_id = filter.get_persona_id()
    return message.push_text(
        id=userId, text=Context.waiting_pair, persona=persona_id)


def paired(userId):
    persona_id = filter.get_persona_id()

    message.push_text(id=userId, persona=persona_id,
                      text=Context.waiting_success[0])
    message.push_quick_reply(
        id=userId, persona=persona_id, text=Context.waiting_success[1])

    message.push_customer_menu(userId, Context.menu_leave)
    return "paired success"


def general_pair(userId):
    persona_id = filter.get_persona_id()
    params = urlencode({"userId": userId})
    web_url_payload = "?".join(["pair.html", params])

    return message.push_button(
        id=userId,
        persona=persona_id,
        text=Context.general_pair_message,
        types="general_pair",
        payload=[web_url_payload],
        title=[Context.general_pair_button]
    )


def quick_pair(userId, placeId, words):
    persona_id = filter.get_persona_id()
    quick_pair_postback = "@".join(["Pair", placeId])
    general_pair_postback = "General_pair"
    return message.push_button(
        id=userId,
        persona=persona_id,
        text=words,
        types="quick_pair",
        payload=[quick_pair_postback, general_pair_postback],
        title=[Context.quick_pair_button, Context.pair_other_button]
    )


def timeout_message(userId):
    persona_id = filter.get_persona_id()
    pair = filter.get_pair(userId)
    pairId = pair.id

    params = urlencode({"pairId": pairId, "userId": userId})
    web_url_payload = "?".join(["message.html", params])

    message.delete_menu(userId)
    message.push_text(id=userId, persona=persona_id,
                      text=Context.timeout_text[0])
    message.push_button(
        id=userId, persona=persona_id,
        text=Context.timeout_text[1],
        types="timeout",
        payload=[web_url_payload, "Quick_pair"],
        title=[Context.send_partner_last_message_button,
               Context.pair_again_button]
    )
    return "reply of timeout"


def last_message(userId, lastWord, hour, minute):
    persona_id = filter.get_persona_id()
    recipient_id = filter.get_recipient_id(userId)
    partner_message = Context.partner_last_message + lastWord
    message.push_text(userId, persona_id,
                      Context.user_last_message + lastWord)
    message.push_text(recipient_id, persona_id,
                      partner_message.format(hour=hour, minute=minute))
    return "sended last message"
