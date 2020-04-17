from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for
import requests

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

    persona = message.requests_get("personas")
    if persona["data"] == []:
        message.persona()

    persona_id = persona["data"][0]["id"]
    message.sender_action(userId, "mark_seen")

    # 接收type=postback的回應
    if "postback" in messaging.keys():
        postback = messaging["postback"]
        payload = postback["payload"]

        if payload == "Start":
            reply.introduction(userId)

            if "referral" in postback.keys():
                ref = postback["referral"]["ref"].split(",")
                entrance = ref[0]
                placeId = ref[1]

                if entrance == "qrcode":
                    reply.qrcode_start_pair(userId, placeId)
                    return "qrcode"
            else:
                reply.general_start_pair(userId):
                return "User started"

        if payload == "Start_pair":
            reply.general_start_pair(userId)
            return "User started"
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
            pair_user(placeId, userId)
            return "User pairing"

    payload = get_status(userId).json
    status = payload["payload"]["status"]

    if status == "unSend":
        reply.timeout(userId)
        return "Send the last message."

    if status == "pairing":
        reply.pairing(userId)
        return "Pairing"

    if "referral" in messaging.keys() and status not in ["paired", "pairing"]:
        ref = messaging["referral"]["ref"].split(",")
        placeId = ref[1]
        reply.qrcode_start_pair(userId, placeId)
        return "qrcode"

    if status == "pairing_fail":
        reply.pair_again(userId, text.wait_expired)
        return "Stop wait"

    if status == "leaved":
        reply.pair_again(userId, text.leave_message)
        return "Leaved"

    if status == "noPair":
        reply.pair_again(userId, text.pair_again_text)
        return "No paired."

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


@bot.route("/pair", methods=["GET"])
def intro_page():
    return render_template("pair.html", place_id_title=text.place_id_title)


@bot.route("/wait/<userId>", methods=["GET"])
def wait_page(userId):
    return render_template("wait.html", cancel_words=text.cancel_pairing_button, userId=userId)


@bot.route("/message/<userId>", methods=["GET"])
def message_page(userId):
    payload = get_status(userId).json
    status = payload["payload"]["status"]
    return render_template("message.html", status=status)


@bot.route("/rule", methods=["GET"])
def rule_page():
    return render_template("rule.html")
