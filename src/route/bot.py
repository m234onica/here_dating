from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for
import requests

from src.db import init_db, db_session
from src.models import Place, Pair
from src.route.api import leave, get_status, pair_user
from src.tool import message, func, text
from config import PAGE_VERIFY_TOKEN, APP_ID, EXPIRED_TIME, BASE_URL


bot = Blueprint("bot", __name__)
init_db()


@bot.route("/webhook", methods=["GET"])
def webhook():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == PAGE_VERIFY_TOKEN:
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
            message.push_text(
                id=userId, text=text.introduction[0], persona=persona_id)

            if "referral" in postback.keys():
                ref = postback["referral"]["ref"].split(",")
                entrance = ref[0]
                placeId = ref[1]

                if entrance == "qrcode":
                    message.push_multi_button(
                        id=userId,
                        persona=persona_id,
                        text=text.qrcode_introduction[0] + text.place_id_title +
                        placeId + text.qrcode_introduction[1],
                        first_title=text.qrcode_check_button,
                        payload="Pair," + placeId,
                        url=BASE_URL + "/pair",
                        sec_title=text.qrcode_intro_button)
                    return "qrcode"
            else:
                message.push_webview(
                    id=userId, text=text.introduction[1], persona=persona_id,
                    webview_page="/pair", title=text.start_chating)

                return "User started"

        if payload == "Start_pair":
            message.push_webview(
                id=userId, text=text.introduction[1], persona=persona_id,
                webview_page="/pair", title=text.start_chating)

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
        message.push_text(id=userId, persona=persona_id,
                          text=text.timeout_text[0])

        message.push_multi_webview(
            id=userId, persona=persona_id,
            text=text.timeout_text[1], first_url=BASE_URL +
            "/message/" + userId,
            first_title=text.send_partner_last_message_button,
            sec_url=BASE_URL + "/pair", sec_title=text.pair_again_button)

        return "Send the last message."

    if status == "pairing":
        message.push_text(userId, persona_id, text.waiting_pair)
        return "Pairing"

    if "referral" in messaging.keys() and status not in ["paired", "pairing"]:
        ref = messaging["referral"]["ref"].split(",")
        placeId = ref[1]
        message.push_multi_button(
            id=userId,
            persona=persona_id,
            text=text.qrcode_introduction[0] + text.place_id_title +
            placeId + text.qrcode_introduction[1],
            first_title=text.qrcode_check_button,
            payload="Pair," + placeId,
            url=BASE_URL + "/pair",
            sec_title=text.qrcode_intro_button)
        return "qrcode"

    if status == "pairing_fail":
        message.push_webview(
            id=userId, text=text.wait_expired,
            persona=persona_id, webview_page="/pair", title=text.pair_again_button)
        return "Stop wait"

    if status == "leaved":
        message.push_webview(
            id=userId, text=text.leave_message,
            persona=persona_id, webview_page="/pair", title=text.pair_again_button)
        return "Leaved"

    if status == "noPair":
        message.push_webview(
            id=userId, text=text.pair_again_text,
            persona=persona_id, webview_page="/pair", title=text.pair_again_button)
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
    return render_template("pair.html", app_id=APP_ID, place_id_title=text.place_id_title)


@bot.route("/wait/<userId>", methods=["GET"])
def wait_page(userId):
    return render_template("wait.html", app_id=APP_ID, expired_time=EXPIRED_TIME)


@bot.route("/message/<userId>", methods=["GET"])
def message_page(userId):
    payload = get_status(userId).json
    status = payload["payload"]["status"]
    return render_template("message.html", status=status, app_id=APP_ID)


@bot.route("/rule", methods=["GET"])
def rule_page():
    return render_template("rule.html", app_id=APP_ID)
