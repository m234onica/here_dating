from src.tool import message
from src.tool import func, text

def introduction(userId):
    persona_id = func.get_persona_id()
    return message.push_text(
        id=userId, text=text.introduction[0], persona=persona_id)


def qrcode_start_pair(userId, placeId):
    persona_id = func.get_persona_id()
    return message.push_button(
        id=userId,
        persona=persona_id,
        text=text.qrcode_introduction[0] + text.place_id_title +
        placeId + text.qrcode_introduction[1],
        types=["postback", "web_url"],
        title=[text.qrcode_check_button,
               text.qrcode_intro_button],
        payload=["Pair," + placeId, "/pair"],
    )


def pair_again(userId, words):
    persona_id = func.get_persona_id()
    return message.push_button(
        id=userId,
        persona=persona_id,
        text=words,
        types=["web_url"],
        payload=["/pair"],
        title=[text.pair_again_button]
    )


def timeout(userId):
    persona_id = func.get_persona_id()

    message.push_text(id=userId, persona=persona_id,
                      text=text.timeout_text[0])
    message.push_button(
        id=userId, persona=persona_id,
        text=text.timeout_text[1],
        types=["web_url", "web_url"],
        payload=["/message/" + userId, "/pair"],
        title=[text.send_partner_last_message_button,
               text.pair_again_button]
    )
    return "reply of timeout"
