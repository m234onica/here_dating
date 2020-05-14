from datetime import datetime, timedelta
from src.tool import filter
from src.models import Pair
from config import Config


def is_pairing(pair):
    if pair.startedAt == None and pair.deletedAt == None:
        return True
    else:
        return False


def is_pair_fail(pair):
    if pair.startedAt == None and pair.deletedAt != None:
        return True
    else:
        return False


def is_paired(pair):
    if pair.startedAt != None and pair.deletedAt == None:
        return True
    else:
        return False


def is_leaved(pair):
    if pair.deletedAt - pair.startedAt < timedelta(minutes=Config.END_TIME):
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