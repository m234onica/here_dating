from flask import Blueprint, render_template, request, json

from src.db import db_session
from src.models import Place, Pair
from src.route import api
from src.tool import message, filter, reply, broken, status, bothook
from src.context import Context
from config import Config


bot = Blueprint("bot", __name__)


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
    postback = bothook.postback(messaging)

    # 已讀
    message.sender_action(userId, "mark_seen")

    if status.is_new_user(userId) or status.is_noPair(userId):
        if postback == None:
            placeId = bothook.referral(messaging)
            # Qrcode
            if placeId != None:
                words = Context.qrcode_introduction
                placeName = filter.get_place_name(placeId)
                return reply.quick_pair(userId, placeId, words.format(placeName=placeName),
                                        Context.qrcode_pair_button, Context.qrcode_other_button)
            # general
            return reply.general_pair(userId, Context.no_pair_message)

        payload = postback["payload"]
        if payload == "Start":
            reply.introduction(userId)
            placeId = bothook.referral(postback)

            # Qrcode
            if placeId != None:
                words = Context.qrcode_introduction
                placeName = filter.get_place_name(placeId)
                return reply.quick_pair(userId, placeId, words.format(placeName=placeName))

            # general
            return reply.general_pair(userId, Context.general_pair_message)

        elif payload == "Quick_pair":
            placeId = filter.get_place_id(userId)
            if placeId == None:
                return reply.general_pair(userId, Context.no_pair_message)
            else:
                words = Context.quick_pairing_message
                placeName = filter.get_place_name(placeId)
                return reply.quick_pair(userId, placeId, words.format(placeName=placeName))

        elif payload == "General_pair":
            return reply.general_pair(userId, Context.general_pair_message)

        elif payload == "Leave":
            return api.leave(userId)

        # 再次進行配對
        else:
            payload = payload.split("@")
            placeId = payload[1]
            return api.pair_user(placeId, userId)

    elif status.is_pairing(userId):
        if postback == None:
            timeout = broken.timeout(userId).json
            paylaod = timeout["payload"]["status"]

            if paylaod == "Broken":
                return "Pairing broken."

            return reply.pairing(userId)

        payload = postback["payload"]
        if payload == "Leave":
            return api.leave(userId)
        else:
            return reply.pairing(userId)

    elif status.is_paired(userId):
        if postback != None:
            payload = postback["payload"]
            if payload == "Leave":
                return api.leave(userId)
            else:
                return reply.paired_warning(userId)

        timeout = broken.timeout(userId).json
        paylaod = timeout["payload"]["status"]

        if paylaod == "Broken":
            return "Pairing broken."

        # tpying action
        recipient_id = filter.get_recipient_id(userId)
        message.sender_action(recipient_id, "typing_on")

        messages = messaging["message"]
        text = bothook.texts(messages)
        attachment = bothook.attachments(messages)

        if text != None:
            push_text = message.push_text(recipient_id, "", text)
            return push_text

        else:
            push_attachment = []
            attachment_url = bothook.attachments(messages)
            for url in attachment_url:
                response = message.push_attachment(
                    recipient_id, "", url)
                push_attachment.append(response)
            return json.dumps(push_attachment)
