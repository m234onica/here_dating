from src.models import Pair


def active_pair():
    return Pair.query.filter(Pair.deletedAt == None)


def recognize_player(userId):

    pair = Pair.query.filter((Pair.playerA == userId) | (
        Pair.playerB == userId)).order_by(Pair.id.desc()).first()

    if userId == pair.playerA:
        return "playerA"

    elif userId == pair.playerB:
        return "playerB"

    else:
        return None


def get_pair(player, userId):

    if player == "playerA":
        return Pair.query.filter(Pair.playerA == userId).order_by(
            Pair.id.desc()).first()

    elif player == "playerB":
        return Pair.query.filter(Pair.playerB == userId).order_by(
            Pair.id.desc()).first()
    else:
        return None


def get_recipient_id(userId):

    player = recognize_player(userId)

    if player == "playerA":
        pair = get_pair(player, userId)
        recipient_id = pair.playerB

    elif player == "playerB":
        pair = get_pair(player, userId)
        recipient_id = pair.playerA
    else:
        recipient_id = None

    return recipient_id
