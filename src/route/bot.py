from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for
import requests

from src.db import init_db, db_session
from src.models import Place, Pair
from src.route.api import leave, get_status
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
    user_info = message.requests_get("/" + userId)

    persona = message.requests_get("/me/personas")
    if persona["data"] == []:
        message.persona()

    persona_id = persona["data"][0]["id"]

    if "postback" in messaging.keys():
        get_payload = messaging["postback"]["payload"]

        if get_payload == "Start":
            message.push_text(
                id=userId, text=text.introduction[0], persona=persona_id)

            message.push_webview(
                id=userId, text=text.introduction[1], persona=persona_id,
                webview_page="/intro", title=text.start_chating)

        # 離開聊天室
        if get_payload == "Leave":

            status = get_status(userId).json

            if status["payload"]["status"] in ["paired", "pairing"]:
                leave(userId)
        return "User leaved"
    

    status = get_status(userId).json
    user_info = message.requests_get("/" + userId)
    print(user_info["first_name"], status)

    
    if status["payload"]["status"] == "unSend":

        message.push_multi_webview(
            id=userId, persona=persona_id,
            text=text.timeout_text[1], first_url=BASE_URL + "/message/" + userId,
            first_title=text.send_partner_last_message_button,
            sec_url=BASE_URL + "/intro", sec_title=text.pair_again_button)

        return "Send the last message."

    if status["payload"]["status"] == "pairing":
        message.push_text(userId, persona_id, text.waiting_pair)
        return "Pairing"

    if status["payload"]["status"] == "wait_expired":
        message.push_webview(
            id=userId, text=text.wait_expired,
            persona=persona_id, webview_page="/intro", title=text.pair_again_button)
        return "Stop wait"

    if status["payload"]["status"] == "leaved":
        message.push_webview(
            id=userId, text=text.leave_message,
            persona=persona_id, webview_page="/intro", title=text.pair_again_button)
        return "Leaved"

    if status["payload"]["status"] == "noPair":
        message.push_webview(
            id=userId, text=text.pair_again_text,
            persona=persona_id, webview_page="/intro", title=text.pair_again_button)
        return "No paired."

    else:
        recipient_id = func.get_recipient_id(userId)

        if "message" in messaging.keys():
            if "text" in messaging["message"].keys():
                message.push_text(recipient_id, None,
                                    messaging["message"]["text"])

            if "attachments" in messaging["message"].keys():
                attachment_url = messaging["message"]["attachments"][0]["payload"]["url"]
                message.push_attachment(
                    recipient_id, None, attachment_url)
    return "ok"


@bot.route("/intro", methods=["GET"])
def intro_page():
    return render_template("intro.html", app_id=APP_ID)


@bot.route("/wait/<userId>", methods=["GET"])
def wait_page(userId):
    return render_template("wait.html", app_id=APP_ID, expired_time=EXPIRED_TIME)


@bot.route("/message/<userId>", methods=["GET"])
def message_page(userId):
    status = get_status(userId).json
    status = status["payload"]["status"]
    return render_template("message.html", status=status, app_id=APP_ID)
