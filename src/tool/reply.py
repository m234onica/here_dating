import os
from urllib.parse import urlencode

from src.tool import message, func
from src.tool.text import Context


def introduction(userId):
    persona_id = func.get_persona_id()
    return message.push_text(
        id=userId, text=Context.introduction[0], persona=persona_id)


def pairing(userId):
    persona_id = func.get_persona_id()
    return message.push_text(
        id=userId, text=Context.waiting_pair, persona=persona_id)


def paired(userId):
    persona_id = func.get_persona_id()

    message.push_text(id=userId, persona=persona_id,
                      text=Context.waiting_success[0])
    message.push_quick_reply(
        id=userId, persona=persona_id, text=Context.waiting_success[1])

    message.push_paired_menu(userId)
    return "paired success"


def general_pair(userId, words):
    persona_id = func.get_persona_id()
    return message.push_button(
        id=userId,
        persona=persona_id,
        text=words,
        types=["web_url"],
        payload=["pair.html"],
        title=[Context.start_chating]
    )


def quick_pair(userId, placeId, words):
    persona_id = func.get_persona_id()
    quick_pair_postback = ",".join(["Pair", placeId])
    general_pair_postback = "General_pair"
    return message.push_button(
        id=userId,
        persona=persona_id,
        text=words,
        types=["postback", "postback"],
        payload=[quick_pair_postback, general_pair_postback],
        title=[Context.qrcode_check_button, Context.qrcode_intro_button]
    )


def timeout(userId):
    persona_id = func.get_persona_id()
    pairId = func.get_pairId(userId)

    params = urlencode({"pairId": pairId, "userId": userId})
    web_url_payload = "?".join(["message.html", params])

    message.delete_menu(userId)
    message.push_text(id=userId, persona=persona_id,
                      text=Context.timeout_text[0])
    message.push_button(
        id=userId, persona=persona_id,
        text=Context.timeout_text[1],
        types=["web_url", "postback"],
        payload=[web_url_payload, "Quick_pair"],
        title=[Context.send_partner_last_message_button,
               Context.pair_again_button]
    )
    return "reply of timeout"


def last_message(userId, lastWord):
    persona_id = func.get_persona_id()
    recipient_id = func.get_recipient_id(userId)

    message.push_text(userId, persona_id,
                      Context.user_last_message + lastWord)
    message.push_text(recipient_id, persona_id,
                      Context.partner_last_message + lastWord)
    return "sended last message"
