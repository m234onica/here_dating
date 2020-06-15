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

### requirements.txt
```
aiohttp==3.6.2
aiomysql==0.0.20
Flask==1.1.1
Flask-Cors==3.0.8
Jinja2==2.10.3
PyMySQL==0.9.2
requests==2.22.0
SQLAlchemy==1.3.12
urllib3==1.25.8
Werkzeug==0.16.0
```

### How it works
```
|- async
    |- delete
        |- message.py           # async post nessebger api
        |- delete.py            # delete pair

    |- pair
        |- message.py           # async post nessebger api
        |- pair.py              # pairing user

    |- main.py                  # GCP main function
    |- run.py                   # local main function

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

### Local build
1. Messenger developers settings
    - 建立 Messener application
    - 新增產品 Webhooks and Messenger
    - 進入 Messenger settings 設定粉專以取得 PAGE_ACCESS_TOKEN 
    - 設定 webhooks 回傳欄位： messages, messaging_postbacks, messaging_referrals, message_reactions
    - 將 PAGE_ACCESS_TOKEN 放到 config.py PAGE_ACCESS_TOKEN
    - 將應用程式編號放到 config.py APP_ID 和 config.js APP_ID

2. Clone here_dating
    ```
    $ pip install -r requirements.txt
    $ npm install
    $ ngrok http 5000

    # config.sample.py 記得加上變數，並改名 config.py
    # /src/static/js/config.sample.js 記得加上變數，並改名 config.js
    # 將ngrok URL 放到 config.py & config.js => BASE_URL

    $ gulp
    # 產生 production static file
    ```

3. 將產生的 static 放上 GCP Storage
    - 建立新的 bucket （權限設為公開）
    - upload static
    - create new folder `image`: 放置圖檔 (robo.png & user_pic.png)
    - 將URL 放到 `config.py STATIC_URL`
    ```
    |- here_dating
        |- image
            |- robo.png
            |- user_pic.png
        |- static
            |- ...
    ```

4. Start here_dating
    ```
    # Here dating main funcion
    $ python3 run.py

    # Pairing's main funcion
    $ python3 pairing_pool/run.py

    # Delete pairs main function
    $ python3 delete/delete.py
    ```
2. Messenger settings
    - 編輯 Webhooks URL `{{ BASE_URL }} + /webhook`
    - Verify token (必須和 `config.py PAGE_VERIFY_TOKEN` 一致)

### Deploy to GCP
1. Cloud functions
    - here_dating
        - trigger: HTTP
        - 用途：作為Here dating webhook，記得將url放到`config.py BASE_URL`
    - pairing_here_pairing
        - trigger: Cloud Pub/Sub
        - topic: pairing_here_dating
    - delete_here_pairing
        - trigger: Cloud Pub/Sub
        - topic: delete_here_dating
3. Cloud Scheduler
    - delete_here_dating
        - Frequency: one minutes (* * * *)
        - Timezone: taipei Standard Time
        - Target: Pub/Sub
    - pairing_here_dating
        - Frequency: one minutes (* * * *)
        - Timezone: taipei Standard Time
        - Target: Pub/Sub

### Others
- Gulpfile.js: 若有改動前端，記得用 `gulp` 來處理模板。