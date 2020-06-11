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
|- delete
    |- delete.py                # delete pair
    |- main.py                  # GCF "delete_here_dating" main funtion

|- pairing_pool
    |- src/message.py           # async post nessebger api
    |- pair.py                  # pairing user
    |- main.py                  # GCF "pairing_here_dating" main funtion

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

### Usage
1. Local
```
# Here dating main funcion
python3 run.py

# Pairing's main funcion
python3 pairing_pool/run.py

# Delete pairs main function
python3 delete/delete.py
```
2. messenger settings
    - 更改webhook URL: `config.BASE_URL/webhook`
    - Verify token (必須和 `config.PAGE_VERIFY_TOKEN` 一致)

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

2. Stroage
    - Bucket name: here_dating
    - file:
        - static: Here dating static file(HTML, JS, CSS)
        - image: Here dating images

### Others
- Gulpfile.js: 若有改動前端，記得用 `gulp` 來處理模板。