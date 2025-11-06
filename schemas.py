from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    """ユーザー作成時のリクエストボディ"""
    name: str
    email: EmailStr  # メール形式バリデーション付き

    class Config:
        json_schema_extra = {
            "example": {
                "name": "山田太郎",
                "email": "yamada@example.com"
            }
        }


class UserUpdate(BaseModel):
    """ユーザー更新時のリクエストボディ"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "山田次郎",
                "email": "yamada.jiro@example.com"
            }
        }


class UserResponse(BaseModel):
    """ユーザー取得時のレスポンス"""
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemyモデルを変換可能にする
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "山田太郎",
                "email": "yamada@example.com",
                "created_at": "2025-11-05T12:34:56"
            }
        }