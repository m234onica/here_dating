from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for
import requests

from src.models import Place, Pair
from src.db import init_db, db_session
from src.sdk import message
from src.route.api import leave, get_status
from config import PAGE_VERIFY_TOKEN, APP_ID


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

    user_id = messaging["sender"]["id"]
    user_info = message.requests_get("/" + user_id)

    persona = message.requests_get("/me/personas")
    if persona["data"] == []:
        message.persona()

    status = get_status(user_id).json
    persona_id = persona["data"][0]["id"]
    
    if "postback" in messaging.keys():
        get_payload = messaging["postback"]["payload"]

        if get_payload == "Start":
            message.push_webview(
                id=user_id,
                text="嗨，" + user_info["first_name"] + "！快來加入聊天吧～",
                webview_page="/intro",
                title="Intro")

            message.push_menu(user_id)

        if get_payload == "Leave":
            if status["payload"]["status"] == "paired":
                recipient_id = status["payload"]["recipient_id"]
                leave(user_id)

                message.push_webview(
                    id=user_id,
                    text="User leave. That's paired again.",
                    webview_page="/intro",
                    title="Pair again")
                
                message.push_webview(
                    id=recipient_id,
                    text="User leave. That's paired again.",
                    webview_page="/intro",
                    title="Pair again")
            else:
                message.push_webview(
                    id=user_id,
                    text="嗨，" + user_info["first_name"] + "！快來加入聊天吧～",
                    webview_page="/intro",
                    title="Intro")
        return "Postback end."
    
    status = get_status(user_id).json

    if "status" in status["payload"].keys():
        if status["payload"]["status"] == "unSend":

            message.push_multi_webview(id=user_id)
            return "Send the last message."

        if status["payload"]["status"] in ["noPair", "pairing", "leaved", "send"]:
            message.push_webview(
                id=user_id,
                text="嗨，" + user_info["first_name"] + "！快來加入聊天吧～",
                webview_page="/intro",
                title="Intro")
            return "No paired."
        
        else:
            recipient_id = status["payload"]["recipient_id"]

            if "message" in messaging.keys():
                if "text" in messaging["message"].keys():
                    message.push_text(recipient_id, persona_id,
                                    messaging["message"]["text"])

                if "attachments" in messaging["message"].keys():
                    attachment_url = messaging["message"]["attachments"][0]["payload"]["url"]
                    message.push_attachment(
                        recipient_id, persona_id, attachment_url)
    return "ok"


@bot.route("/intro", methods=["GET"])
def intro_page():
    return render_template("intro.html", app_id=APP_ID)


@bot.route("/wait", methods=["GET"])
def wait_page():
    return render_template("wait.html", app_id=APP_ID)


@bot.route("/message", methods=["GET"])
def leave_page():
    return render_template("message.html", app_id=APP_ID)
