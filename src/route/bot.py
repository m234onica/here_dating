from flask import Blueprint, render_template, request

from src.db import init_db, db_session
from src.models import Place, Pair
from src.route.api import leave, get_status, pair_user
from src.tool import message, func, text, reply
from config import Config


bot = Blueprint("bot", __name__)
init_db()


@bot.route("/webhook", methods=["GET"])
def webhook():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == Config.PAGE_VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Verification success", 200


@bot.route("/webhook", methods=["POST"])
def webhook_handle():
    data = request.get_json()
    messaging = data["entry"][0]["messaging"][0]
    userId = messaging["sender"]["id"]
    placeId = func.get_placeId(userId)

    message.sender_action(userId, "mark_seen")

    # 接收type=postback的回應
    if "postback" in messaging.keys():
        postback = messaging["postback"]
        payload = postback["payload"]

        if payload == "Start":
            reply.introduction(userId)

            if "referral" in postback.keys():
                referral = postback["referral"]["ref"].split(",")
                entrance = referral[0]
                placeId = referral[1]

                if entrance == "qrcode":
                    return reply.qrcode_start_pair(userId, placeId)
            else:
                return reply.general_start_pair(userId)

        if payload == "Quick_pair":
            return reply.quick_pair(userId, placeId,
                                    text.quick_pairing_message.format(placeId=placeid))

        # 離開聊天室
        if payload == "Leave":
            payload = get_status(userId).json
            status = payload["payload"]["status"]

            if status in ["paired", "pairing"]:
                leave(userId)
            return "User leaved"

        payload_param = payload.split(",")
        placeId = payload_param[1]

        if payload_param[0] == "Pair":
            return pair_user(placeId, userId)

    payload = get_status(userId).json
    status = payload["payload"]["status"]

    if status == "pairing":
        return reply.pairing(userId)

    if "referral" in messaging.keys() and status not in ["paired", "pairing"]:
        referral = messaging["referral"]["ref"].split(",")
        placeId = referral[1]
        return reply.qrcode_start_pair(userId, placeId)

    if status in ["pairing_fail", "leaved", "noPair", "unSend"]:
        if placeId != None:
            words = text.quick_pairing_message
            return reply.quick_pair(userId, placeId,
                                    words.format(placeId=placeId))

        else:
            return reply.pair_again(userId, text.introduction[1])
    else:
        recipient_id = func.get_recipient_id(userId)
        timeout = func.timeout_chat(userId).json

        if timeout["payload"]["status"] == "paired" and "message" in messaging.keys():
            # if "reply_to" in messaging["message"].keys():

            if "text" in messaging["message"].keys():
                message.sender_action(recipient_id, "typing_on")
                message.push_text(recipient_id, None,
                                  messaging["message"]["text"])

            if "attachments" in messaging["message"].keys():
                attachment_url = messaging["message"]["attachments"][0]["payload"]["url"]
                message.sender_action(recipient_id, "typing-on")
                message.push_attachment(
                    recipient_id, None, attachment_url)
        return "Send message"

    return "ok"