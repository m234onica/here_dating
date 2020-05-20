def postback(messaging):
    if "postback" in messaging.keys():
        return messaging["postback"]
    else:
        return None


def referral(postback):
    if "referral" in postback.keys():
        referral = postback["referral"]["ref"].split("@")
        return referral[1]
    else:
        return None


def texts(message):
    if "text" in message.keys():
        return message["text"]
    else:
        return None


def attachments(message):
    if "attachments" in message.keys():
        return message["attachments"][0]["payload"]["url"]
    else:
        return None
