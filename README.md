# here-dating

### Tables
- place
```
    id                  VARCHAR( 50 )       NOT NULL,
    name                VARCHAR( 50 )       NOT NULL,
    longitude           DECIMAL( 10, 6 )    NOT NULL,   -- 經度
    latitude            DECIMAL( 10, 6 )    NOT NULL,   -- 緯度
    PRIMARY KEY( id )
```
- pair
```
    id                  INT                 NOT NULL    AUTO_INCREMENT,
    placeId             VARCHAR( 50 )       NOT NULL,
    playerA             VARCHAR( 100 )      NOT NULL,
    playerB             VARCHAR( 100 ),
    createdAt           DATETIME        	NOT NULL    DEFAULT  CURRENT_TIMESTAMP,
    deletedAt           DATETIME,                                -- 結束配對的時間
    playerA_lastedAt    DATETIME,                                -- plyaerA留遺言的時間
    playerB_lastedAt    DATETIME,                                -- plyaerB留遺言的時間
    status              ENUM("wait_expired", "leave", "end"),    -- 僅供數據分析使用
    PRIMARY KEY( id )
```
- pool
```
    id                  INT                 NOT NULL    AUTO_INCREMENT,
    placeId             VARCHAR( 50 )       NOT NULL,
    userId              VARCHAR( 100 )      NOT NULL,
    createdAt           DATETIME        	NOT NULL    DEFAULT CURRENT_TIMESTAMP,
    deletedAt           DATETIME,                                                   
    status              BOOLEAN             NOT NULL    DEFAULT 0    
    PRIMARY KEY( id )
```

### How it works
```
|- async
    |- delete.py                # delete pair
    |- pair.py                  # pair user
    |- run.py                   # delete and pairing main funciton
    |- main.py                  # delete and pairing in GCF

|- src
    |- static/data
        |- data.json.jinja      # messenger api's templates
        |- text.json            # front-end's words
    |- route
        |- api.py               # here_dating's api
        |- bot.py               # messenger bot webhook
    |- tool
        |- bothook.py           # webhook response's payload
        |- broken.py            # delete pairs in manual
        |- filter.py            # data filtering
        |- status.py            # user's status
        |- message.py           # messenge's json
        |- reply.py             # sending message to user

    |- context.py               # here dating's words
    |- db.py                    # database's engine
    |- models.py                # database's model

|- main.py                      # here dating in GCF
|- run.py                       # main function
|- gulpfile.js                  # build front-end
```

### Config
```
    EXPIRED_TIME        # 尋找配對的時間到期
    END_TIME            # 配對聊天的時間到期

    SECRET_KEY          # 記得改自己的KEY

    # 可在 Messenger setting 取得
    APP_ID              # messenger ID
    PAGE_ACCESS_TOKEN   # messenger token

    BASE_URL            # front-end call api's url
    STATIC_URL          # webview link
```

### Usage
```
python3 run.py

python3 async/run.py
```

### GCP
1. Cloud functions
    - here_dating
        - trigger: HTTP
    - async_here_pairing (sub/pub)
        - trigger: Cloud Pub/Sub
        - topic: here_dating_schedule
2. Stroage
    - here_dating
        - static
        - image

### Others
- Gulpfile.js
若有改動前端，記得用 `gulp` 來處理模板。
- cors-json-file.json
`gsutil cors set cors-json-file.json gs://here_dating`

