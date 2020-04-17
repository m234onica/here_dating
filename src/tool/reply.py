from src.tool import message
from src.tool import func, text

def pair_again(userId, words):
    persona_id = func.get_persona_id()
    return message.push_button(
        id=userId,
        persona=persona_id,
        text=words,
        types=["web_url"],
        payload=["/pair"],
        title=[text.pair_again_button]
    )