from datetime import datetime, timedelta
from src.tool import filter
from src.models import Pair, Place
from config import Config


def is_noPair(userId):
    pair = filter.get_active_pair(userId)
    pool = filter.get_active_pool(userId)

    if pair == None and pool == None:
        return True
    else:
        return False


def is_pairing(userId):
    pool = filter.get_active_pool(userId)
    if pool != None:
        return True
    else:
        return False


def is_paired(userId):
    pair = filter.get_active_pair(userId)
    if pair != None:
        return True
    else:
        return False


def is_send_last_message(userId):
    pair = filter.get_pair(userId)
    if pair.playerA == userId:
        if pair.playerA_lastedAt != None:
            return True
        return False
    else:
        if pair.playerB_lastedAt != None:
            return True
        return False


def is_place(placeId):
    place = Place.query.filter(Place.id == placeId).first()
    if place == None:
        return False
    else:
        return True