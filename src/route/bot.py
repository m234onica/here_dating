from flask import Blueprint, render_template, request

from src.db import init_db, db_session
from src.models import Place, Pair
from src.route import api
from src.tool import message, filter, reply, broken, status, bothook
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

    # 已讀
    message.sender_action(userId, "mark_seen")

    # 接收type=postback的回應
    postback = bothook.postback(messaging)
    if postback != None:
        if status.is_pairing(userId):
            return reply.pairing(userId)
        elif status.is_paired:
            return reply.paired_warning(userId)

        payload = postback["payload"]
        if payload == "Start":
            reply.introduction(userId)

            # qrcode
            placeId = bothook.referral(postback)
            if placeId != None:
                words = Context.qrcode_introduction
                placeName = filter.get_place_name(placeId)
                return reply.quick_pair(userId, placeId, words.format(placeName=placeName))

            # general
            return reply.general_pair(userId, Context.general_pair_message)

        elif payload == "Quick_pair":
            if status.is_new_user(userId):
                return reply.general_pair(userId, Context.no_pair_message)
            else:
                words = Context.quick_pairing_message
                placeId = filter.get_place_id(userId)
                placeName = filter.get_place_name(placeId)
                return reply.quick_pair(userId, placeId, words.format(placeName=placeName))

        elif payload == "General_pair":
            return reply.general_pair(userId, Context.general_pair_message)

        elif payload == "Leave":
            if status.is_pairing(userId) or status.is_paired(userId):
                return api.leave(userId)
            else:
                return "User has no pair to leave"
 
        else:
            if status.is_new_user(userId):
                return reply.general_pair(userId, Context.no_pair_message)
            else:
                payload = payload.split("@")
                placeId = payload[1]
                return api.pair_user(placeId, userId)
    else:
        # 傳送聊天訊息or附件
        if status.is_noPair(userId):
            placeId = bothook.referral(messaging)
            if placeId != None:
                words = Context.qrcode_introduction
                placeName = filter.get_place_name(placeId)
                return reply.quick_pair(userId, placeId, words.format(placeName=placeName))
            else:
                return reply.general_pair(userId, Context.no_pair_message)


        elif status.is_pairing(userId) or status.is_paired(userId):
            timeout = broken.timeout(userId).json
            paylaod = timeout["payload"]["status"]

            if paylaod == "pairing":
                return reply.pairing(userId)

            elif paylaod == "paired":
                # tpying action
                recipient_id = filter.get_recipient_id(userId)
                message.sender_action(recipient_id, "typing_on")

                messages = messaging["message"]
                text = bothook.texts(messages)
                attachment = bothook.attachments(messages)

                if text != None:
                    return message.push_text(recipient_id, "", text)

                if attachment != None:
                    attachment_url = bothook.attachments(messages)
                    return message.push_attachment(
                        recipient_id, "", attachment_url)

            return "Send message"
