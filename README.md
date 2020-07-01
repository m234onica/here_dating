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

### Local build

前置作業：run ngrok

    $ ngrok http 5000

**Build here_dating**

    $ git clone git@github.com:momokatw/here-dating.git

    # create virtual env and active
    $ pip install -r requirements.txt

    $ cp config.sample.py config.py
    # Edit config: mysql, SECRET_KEY, PAGE_VERIFY_TOKEN, PAGE_ACCESS_TOKEN(從messenger取得，稍後解釋)
    # BASE_URL: 將 ngrok url 放上
    # STATIC_URL: 將前端的 url 放上

    $ python3 run.py

**Messenger developers settings**
- 建立 Messener application
- 新增產品 Webhooks, Messenger
- Messenger
    - 連結粉專
    - 產生權杖 access token（並將此 token 放上 `config.py` PAGE_ACCESS_TOKEN）
    - 新增回呼網址：放上 `ngrok url + /webhook` (eg. `https://xxx.ngrok/webhook`)，以及 PAGE_VERIFY_TOKEN，驗證並儲存
    - 新增訂閱欄位
        - messages
        - messaging_postbacks
        - messaging_referrals
        - message_reactions
- 到這裡就能去messenger bot測試訊息了。

**Build Static file**

    $ npm install gulp -g
    $ npm install
    $ cp src/static/js/config.sample.js src/static/js/config.js
    # edit config.js
    # APP_ID: 應用程式編號，在Messenger developers settings 可取得
    # BASE_URL: 放上ngrok url

    $ mkdir static
    $ gulp

- 想在本地端測試static file的話，修改flask template_folder & static_folder 路徑即可

**Bulid async_here_dating**

    $ cp config.py async_func/config.py
    $ python3 async_func/run.py

**將產生的 static 放上 GCP Storage**

- 建立新的 bucket （權限設為公開）
- upload `./static/**`
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

**Start here_dating**
```
# Here dating main funcion
$ python3 run.py

# async's main funcion
$ python3 async_func/run.py
```

### Deploy to GCP
1. Cloud functions
    - here_dating
        - trigger: HTTP
        - 用途：作為Here dating webhook，記得將url放到`config.py BASE_URL`
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