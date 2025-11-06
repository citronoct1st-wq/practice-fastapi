from sqlalchemy import Column, Integer, String, DateTime, func
from datetime import datetime
from database import Base

class User(Base):
    """ユーザーモデル"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self):
        """デバッグ用の表示"""
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"