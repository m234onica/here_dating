from flask import Blueprint, render_template, request

from src.db import init_db, db_session
from src.models import Place, Pair
from src.route.api import leave, get_status, pair_user
from src.tool import message, filter, reply, broken
from src.context import Context
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

    message.sender_action(userId, "mark_seen")

    # 接收type=postback的回應
    if "postback" in messaging.keys():
        postback = messaging["postback"]
        payload = postback["payload"]

        if payload == "Start":
            reply.introduction(userId)

            if "referral" in postback.keys():
                referral = postback["referral"]["ref"].split("@")
                entrance = referral[0]
                placeId = referral[1]
                if entrance == "qrcode":
                    words = Context.qrcode_introduction
                    return reply.quick_pair(userId, placeId, words.format(placeId=placeId))
            else:
                return reply.general_pair(userId, Context.introduction[1])

        if payload == "Quick_pair":
            words = Context.quick_pairing_message
            placeId = filter.get_place_id(userId)
            return reply.quick_pair(userId, placeId, words.format(placeId=placeId))

        if payload == "General_pair":
            return reply.general_pair(userId, Context.introduction[1])

        # 離開聊天室
        if payload == "Leave":
            payload = get_status(userId).json
            status = payload["payload"]["status"]

            if status in ["paired", "pairing"]:
                leave(userId)
            return "User leaved"

        payload_param = payload.split("@")
        placeId = payload_param[1]

        if payload_param[0] == "Pair":
            return pair_user(placeId, userId)

    payload = get_status(userId).json
    status = payload["payload"]["status"]

    if status == "pairing":
        return reply.pairing(userId)

    if status in ["pairing_fail", "leaved", "noPair", "unSend"]:
        if "referral" in messaging.keys():
            referral = messaging["referral"]["ref"].split("@")
            placeId = referral[1]
            words = Context.qrcode_introduction
            return reply.quick_pair(userId, placeId, words.format(placeId=placeId))

        return reply.general_pair(userId, Context.introduction[1])

    else:
        recipient_id = filter.get_recipient_id(userId)
        timeout = broken.timeout(userId).json

        if timeout["payload"]["status"] == "paired" and "message" in messaging.keys():

            if "text" in messaging["message"].keys():
                message.sender_action(recipient_id, "typing_on")
                message.push_text(recipient_id, "",
                                  messaging["message"]["text"])

            if "attachments" in messaging["message"].keys():
                attachment_url = messaging["message"]["attachments"][0]["payload"]["url"]
                message.sender_action(recipient_id, "typing-on")
                message.push_attachment(
                    recipient_id, "", attachment_url)
        return "Send message"

    return "ok"
