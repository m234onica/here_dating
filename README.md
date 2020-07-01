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
    playerA_lastedAt    DATETIME,                                -- plyaerA 留遺言的時間
    playerB_lastedAt    DATETIME,                                -- plyaerB 留遺言的時間
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
|- async_func
    |- delete
        |- message.py           # async post nessebger api
        |- delete.py            # delete pair

    |- pair
        |- message.py           # async post nessebger api
        |- pair.py              # pairing user
        |- select.py            # select data

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
### Toolkit
    python3.7
    pip3
    npm
    node
    gulp

### Local build

**前置作業**
1. run ngrok
    ```
    $ ngrok http 5000
    ```

2. Messenger developers settings
    - 建立 Messener application
    - 新增產品 Webhooks, Messenger
    - Messenger
        - 新增粉專
        - 產生權杖 access token

**Build Static file**

    $ npm install gulp -g
    $ npm install
    $ cp src/static/js/config.sample.js src/static/js/config.js
    # edit config.js
    # APP_ID: 應用程式編號，在 Messenger developers settings 可取得
    # BASE_URL: 放上 ngrok url

    $ mkdir static
    $ gulp

**將產生的 static 放上 GCP Storage**

- 建立新的 bucket （權限設為公開）
- upload `./static/**`
- create new folder `image`: 放置圖檔 (robo.png & user_pic.png)
```
|- here_dating
    |- image
        |- robo.png
        |- user_pic.png
    |- static
        |- ...
```

**Build here_dating**

    $ git clone git@github.com:momokatw/here-dating.git

    # create virtual env and active
    $ pip3 install -r requirements.txt

    $ cp config.sample.py config.py
    # Edit config: mysql, SECRET_KEY, PAGE_VERIFY_TOKEN
    # PAGE_ACCESS_TOKEN: Messenger's access token
    # BASE_URL: ngrok url
    # STATIC_URL: GCP storage's url + /here_dating/static/templates

    $ python3 run.py


**Verify Messenger Webhook**

- Messenger settings
    - 新增回呼網址：放上 `ngrok url + /webhook` (eg. `https://xxx.ngrok/webhook`)，以及 PAGE_VERIFY_TOKEN，驗證並儲存
    - 新增訂閱欄位
        - messages
        - messaging_postbacks
        - messaging_referrals
        - message_reactions

**Test in Local**

基於 Google Storage 有不可抗力的快取因素，在本地端測試 webview 會比較快速。
```
# src/__init__.py
    app = Flask(__name__, template_folder="../static/templates", static_folder="../static/js")

# config.py
    STATIC_URL 改成 ngrok url (同 BASE_URL)
```

**Bulid async_here_dating**

    $ cp config.py async_func/config.py
    $ python3 async_func/run.py

### Deploy to GCP

1. Cloud functions
    - here_dating
        - trigger: HTTP
        - 用途：作為 Here dating webhook，記得將 url 放到 `config.py BASE_URL`
    - async_here_dating
        - trigger: Cloud Pub/Sub
        - topic: async_here_dating
2. Cloud Scheduler
    - async_here_dating
        - Frequency: one minutes (* * * *)
        - Timezone: taipei Standard Time
        - Target: Pub/Sub

### Others
- Gulpfile.js: 若有改動前端，記得用 `gulp` 來處理模板。