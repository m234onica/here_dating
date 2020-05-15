from flask import Blueprint, render_template, request

from src.db import init_db, db_session
from src.models import Place, Pair
from src.route.api import leave, get_status, pair_user
from src.tool import message, filter, reply, broken, status
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
    pair = filter.get_pair(userId)

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
                return reply.general_pair(userId)

        if payload == "Quick_pair":
            words = Context.quick_pairing_message
            placeId = filter.get_place_id(userId)
            return reply.quick_pair(userId, placeId, words.format(placeId=placeId))

        if payload == "General_pair":
            return reply.general_pair(userId)

        # 離開聊天室
        if payload == "Leave":
            if status.is_pairing(pair) or status.is_paired(pair):
                leave(userId)
            return "User leaved"

        payload = payload.split("@")
        if payload[0] == "Pair":
            placeId = payload[1]
            return pair_user(placeId, userId)

    if status.is_noPair(pair):
        return reply.general_pair(userId)

    if status.is_pairing(pair):
        timeout = broken.timeout(userId).json
        if timeout["payload"]["status"] == "pairing":
            return reply.pairing(userId)
        else:
            return "pairing broken"

    if not (status.is_pairing(pair) or status.is_paired(pair)):
        if "referral" in messaging.keys():
            referral = messaging["referral"]["ref"].split("@")
            placeId = referral[1]
            words = Context.qrcode_introduction
            return reply.quick_pair(userId, placeId, words.format(placeId=placeId))
        return reply.general_pair(userId)

    if status.is_paired(pair):
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
