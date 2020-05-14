class Context:
    menu_start = "開始使用"
    menu_rule = "規則說明"
    menu_leave = "我想離開"
    menu_waiting_cancel = "取消等待"

    introduction = "您好，歡迎進入 HereDating！這是一個可以與同一個地點或活動的陌生人匿名聊天的小遊戲 ，每場聊天限時十分鐘。"
    general_pair_message = "目前 HereDating 僅提供特定地點使用，請點選下方按鈕開啟頁面，輸入地標編號來與大家匿名聊天吧！"
    general_pair_button = "開始使用"

    qrcode_introduction = "您目前的地標編號為「{placeId}」，是否加入呢？"
    place_id_title = "#好奇心"
    qrcode_check_button = "確定"
    qrcode_intro_button = "使用其他編號"

    quick_pair_button = "再次進行配對"
    pair_other_button = "使用其他編號"

    waiting_pair = "正在為你找人中，請稍候。\n對規則有疑問可以在右下角觀看說明"
    wait_expired = "由於超過 2 分鐘沒有找到聊天對象，小天使跟你說掰掰囉。若想重新尋找聊天對象請再次按下按鈕開始聊天。"
    waiting_leave = "你已經離開交誼廳了，要不要重新開始找人聊天呢？"
    waiting_success = ["已為你找到聊天對象囉！現在開始你們有10分鐘可以聊天認識，把握時間。", "先試著說聲「Hi」吧！"]


    leave_message = "你已經離開對話了，要不要再重新找人聊天呢？"
    partner_leave_message = "哎呀！對方選擇離開對話，要不要再重新找人聊天呢？"

    timeout_text = ["聊天時間到囉！你已離開交誼廳，剛剛聊得愉快嗎？",
                    "現在開始你有 3 分鐘的時間可以留下最後一段話給對方，如果覺得聊天過程很愉快，不妨和對方交個朋友吧！"]
    send_partner_last_message_button = "留下最後一段話"

    user_last_message = "這是我傳的遺言："
    partner_last_message = "這是{hour}點{minute}分傳來的最後一段話：\n"
    # partner_last_message = "這是{hour}點{minute}分的{user_first_name}傳來的最後一段話：\n"
    pair_again_button = "我要開啟新對話"
    pair_again_text = "請問您想要找下個人聊天，再認識一位新朋友嗎？"

    quick_pairing_message = "您上一次配對的地標編號為「{placeId}」，是否要使用此編號進行快速配對？"

    cancel_pairing_button = "我想離開"
    cancel_pairing_postback = "好的，期待下次與你見面唷！"
