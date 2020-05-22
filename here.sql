USE hereDB;
CREATE TABLE place(
    id                  VARCHAR( 50 )       NOT NULL,
    name                VARCHAR( 50 )       NOT NULL,
    longitude           DECIMAL( 10, 6 )    NOT NULL,   -- 經度
    latitude            DECIMAL( 10, 6 )    NOT NULL,   -- 緯度
    PRIMARY KEY( id )
);

CREATE TABLE pair(
    id                  INT                 NOT NULL    AUTO_INCREMENT,
    placeId             VARCHAR( 50 )       NOT NULL,
    playerA             VARCHAR( 100 )      NOT NULL,
    playerB             VARCHAR( 100 ),
    createdAt           DATETIME        	NOT NULL    DEFAULT     CURRENT_TIMESTAMP,
    startedAt           DATETIME,                                                   -- 開始聊天的時間
    deletedAt           DATETIME,                                                   -- 結束聊天的時間
    playerA_lastedAt    DATETIME,                                                   -- plyaerA留遺言的時間
    playerB_lastedAt    DATETIME,                                                   -- plyaerB留遺言的時間
    status              ENUM("wait_expired", "leave", "end"),                       -- 僅供數據分析使用
    PRIMARY KEY( id )
);

CREATE TABLE pool(
    id                  INT                 NOT NULL    AUTO_INCREMENT,
    placeId             VARCHAR( 50 )       NOT NULL,
    userId              VARCHAR( 100 )      NOT NULL,
    createdAt           DATETIME        	NOT NULL    DEFAULT CURRENT_TIMESTAMP,
    deletedAt           DATETIME,                                                   
    status              BOOLEAN             NOT NULL    DEFAULT 0    
    PRIMARY KEY( id )
);

INSERT INTO place (id, name, longitude, latitude) VALUE ("2322", "木木卡門市", 25.066765, 121.526336);
INSERT INTO pair (placeId, playerA) VALUE ("2332", "3564003720340673");
