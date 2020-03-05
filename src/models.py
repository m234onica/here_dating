from sqlalchemy import Column, String, DateTime, Enum, Integer, DECIMAL, func
from sqlalchemy.dialects import mysql
from src.db import Base

import enum

class status_Enum(enum.Enum):
    wait_expired = 0
    leave = 1
    end = 2

class Place(Base):
    __tablename__ = 'place'
    id = Column(Integer, primary_key=True, comment="商店代號")
    name = Column(String(50), nullable=False, comment="商店名")
    longitude = Column(DECIMAL(10, 6), nullable=False, comment="經度")
    latitude = Column(DECIMAL(10, 6), nullable=False, comment="緯度")

    def __repr__(self):
        return "<Place: %r, %r, %r, %r>".format(self.id, self.name, self.longitude, self.latitude)


class Pair(Base):
    __tablename__ = 'pair'
    id = Column(Integer, primary_key=True, comment="配對代號")
    placeId = Column(Integer, nullable=False, comment="商店代號")
    playerA = Column(String(100), nullable=False, comment="使用者A")
    playerB = Column(String(100), nullable=True, comment="使用者B")
    createdAt = Column(DateTime, nullable=False,server_default=func.now(), comment='建立時間')
    startedAt = Column(DateTime, nullable=True, comment='建立時間')
    deletedAt = Column(DateTime, nullable=True, comment='刪除時間')
    status = Column(Enum(status_Enum), nullable=True, comment="此配對狀態，僅供數據分析使用")
    

    def __repr__(self):
        return "<Pair: {}, {}, {}, {}>".format(self.id, self.placeId, self.playerA, self.playerB)

