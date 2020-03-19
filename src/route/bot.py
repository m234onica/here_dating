from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for
import requests

from src.db import init_db, db_session
from src.models import Place, Pair
from src.route.api import leave, get_status
from src.tool import message, func
from config import PAGE_VERIFY_TOKEN, APP_ID, EXPIRED_TIME


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
            message.push_webview(
                id=userId, text="嗨，" + user_info["first_name"] + "！快來加入聊天吧～", persona=persona_id,
                webview_page="/intro", title="Intro")

            message.push_menu(userId)

        # 離開聊天室
        if get_payload == "Leave":

            status = get_status(userId).json
            
            if status["payload"]["status"] == "paired":
                recipient_id = func.get_recipient_id(userId)
                leave(userId)

                message.push_webview(
                    id=userId, text="User leave. That's paired again.", persona=persona_id,
                    webview_page="/intro", title="Pair again")

                message.push_webview(
                    id=recipient_id, text="User leave. That's paired again.", persona=persona_id,
                    webview_page="/intro", title="Pair again")

                return "User leaved"

    status = get_status(userId).json
    print(status)
    if "status" in status["payload"].keys():
        if status["payload"]["status"] == "unSend":
            
            message.push_multi_webview(id=userId, persona=persona_id)
            return "Send the last message."

        if status["payload"]["status"] == "pairing":
            message.push_text(userId, persona_id, "配對中，請稍等...")

        if status["payload"]["status"] in ["noPair", "leaved"]:
            message.push_webview(
                id=userId, text="嗨，" + user_info["first_name"] + "！快來加入聊天吧～",
                persona=persona_id, webview_page="/intro", title="Intro")
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
