from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for

from src.models import Place, Pair
from src.db import init_db, db_session
from config import PAGE_ACCESS_TOKEN, PAGE_VERIFY_TOKEN, FB_API_URL, BASE_URL, APP_ID


bot = Blueprint('bot', __name__)
init_db()


@bot.route('/webhook', methods=['GET'])
def webhook():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == PAGE_VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Verification success", 200


@bot.route("/webhook", methods=['POST'])
def webhook_handle():
    data = request.get_json()
    messaging = data['entry'][0]['messaging'][0]
    return 'ok'