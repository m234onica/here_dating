from urllib.parse import urlencode

from src.tool import message
from src.tool import func, text


def introduction(userId):
    persona_id = func.get_persona_id()
    return message.push_text(
        id=userId, text=text.introduction[0], persona=persona_id)


def general_start_pair(userId):
    persona_id = func.get_persona_id()
    return message.push_button(
        id=userId,
        text=text.introduction[1],
        persona=persona_id,
        types=["web_url"],
        payload=["pair"],
        title=[text.start_chating]
    )


def qrcode_start_pair(userId, placeId):
    persona_id = func.get_persona_id()
    words = text.qrcode_introduction
    return message.push_button(
        id=userId,
        persona=persona_id,
        text=words.format(placeId=placeId),
        types=["postback", "web_url"],
        title=[text.qrcode_check_button,
               text.qrcode_intro_button],
        payload=["Pair," + placeId, "pair"],
    )


def pairing(userId):
    persona_id = func.get_persona_id()
    return message.push_text(
        id=userId, text=text.waiting_pair, persona=persona_id)


def paired(userId):
    persona_id = func.get_persona_id()

    message.push_text(id=userId, persona=persona_id,
                      text=text.waiting_success[0])
    message.push_quick_reply(
        id=userId, persona=persona_id, text=text.waiting_success[1])

    message.push_paired_menu(userId)
    return "paired success"


def pair_again(userId, words):
    persona_id = func.get_persona_id()
    return message.push_button(
        id=userId,
        persona=persona_id,
        text=words,
        types=["web_url"],
        payload=["pair"],
        title=[text.pair_again_button]
    )


def quick_pair(userId, placeId, words):
    persona_id = func.get_persona_id()
    postback_payload = func.concat("Pair", placeId, sep=",")
    return message.push_button(
        id=userId,
        persona=persona_id,
        text=words,
        types=["postback", "web_url"],
        payload=[postback_payload, "pair"],
        title=[text.qrcode_check_button, text.qrcode_intro_button]
    )


def timeout(userId):
    persona_id = func.get_persona_id()
    pairId = func.get_pairId(userId)

    params = urlencode({"pairId": pairId, "userId": userId})
    web_url_payload = func.concat("message", params, sep="?")

    message.push_text(id=userId, persona=persona_id,
                      text=text.timeout_text[0])
    message.push_button(
        id=userId, persona=persona_id,
        text=text.timeout_text[1],
        types=["web_url", "postback"],
        payload=[web_url_payload, "Quick_pair"],
        title=[text.send_partner_last_message_button,
               text.pair_again_button]
    )
    return "reply of timeout"


def last_message(userId, lastWord):
    persona_id = func.get_persona_id()
    recipient_id = func.get_recipient_id(userId)

    message.push_text(userId, persona_id,
                      text.user_last_message + lastWord)
    message.push_text(recipient_id, persona_id,
                      text.partner_last_message + lastWord)
    return "sended last message"
