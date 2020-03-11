from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for
import requests

from src.models import Place, Pair
from src.db import init_db, db_session
from src.sdk import message
from src.route.api import leave
from config import PAGE_VERIFY_TOKEN, APP_ID, FB_API_URL, PAGE_ACCESS_TOKEN


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

    user_info = requests.get(
        FB_API_URL + "/" + user_id + "?access_token=" + PAGE_ACCESS_TOKEN).json()

    persona = requests.get(FB_API_URL + "/me/personas?access_token=" + PAGE_ACCESS_TOKEN).json()
    if persona["data"] == []:
        message.persona()
        
    persona_id = persona["data"][0]["id"]

    if "postback" in messaging.keys():
        get_payload = messaging["postback"]["payload"]
        if get_payload == "GET_STARTED_PAYLOAD":
            message.push_webview(user_id, user_info["first_name"], "/intro")
            message.push_menu(user_id)


    if "message" in messaging.keys():
        if "text" in messaging["message"].keys():

            if messaging["message"]["text"] == "Leave":
                leave(user_id)
                return "Pairing is the end."

            else:
                pair = Pair.query.filter((Pair.playerA == user_id) | (Pair.playerB == user_id)).\
                        filter(Pair.deletedAt == None).first()

            if pair == None:
                message.push_text(user_id, None, "This chat is the end.")
                return "Pairing is the end."
            else:
                if user_id != pair.playerA:
                    recipient_id = pair.playerA

                else: 
                    recipient_id = pair.playerB

                message.push_text(recipient_id, persona_id, messaging["message"]["text"])
    
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
