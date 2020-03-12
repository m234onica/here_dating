from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for
import requests

from src.models import Place, Pair
from src.db import init_db, db_session
from src.sdk import message
from src.route.api import leave
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

    persona_id = persona["data"][0]["id"]

    pair = Pair.query.filter(
        (Pair.playerA == user_id) | (Pair.playerB == user_id))

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
            if pair.filter(Pair.deletedAt == None):
                leave(user_id)

            delete = pair.filter(Pair.deletedAt != None).first()

            message.push_webview(
                id=delete.playerA,
                text="User leave. That's paired again.",
                webview_page="/intro",
                title="Pair")

            message.push_webview(
                id=delete.playerB,
                text="User leave. That's paired again.",
                webview_page="/intro",
                title="Pair")

            return "Pairing is the end."

    if pair.first() == None:
        message.push_webview(
            id=user_id,
            text="嗨，" + user_info["first_name"] + "！快來加入聊天吧～",
            webview_page="/intro",
            title="Intro")
        return "No paired."

    active_pair = pair.filter(Pair.deletedAt == None).first()

    if active_pair == None:
        message.push_webview(
            id=user_id,
            text="No paired. That's pair !",
            webview_page="/intro",
            title="Pair")

    else:
        if user_id != active_pair.playerA:
            recipient_id = active_pair.playerA

        else:
            recipient_id = active_pair.playerB

        if "message" in messaging.keys():
            if "text" in messaging["message"].keys():
                
                message.push_text(recipient_id, persona_id,
                                  messaging["message"]["text"])

            if "attachments" in messaging["message"].keys():

                message.push_attachment(
                    recipient_id, persona_id, messaging["message"]["attachments"][0]["payload"]["url"])
    return "ok"


@bot.route("/intro", methods=["GET"])
def intro_page():
    return render_template("intro.html", app_id=APP_ID)


@bot.route("/wait", methods=["GET"])
def wait_page():
    return render_template("wait.html", app_id=APP_ID)


@bot.route("/leave", methods=["GET"])
def leave_page():
    return render_template("leave.html", app_id=APP_ID)
