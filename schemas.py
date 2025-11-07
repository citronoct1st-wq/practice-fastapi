from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# ========== ユーザー作成時スキーマ ==========
class UserCreate(BaseModel):
    """ユーザー作成リクエスト"""
    name: str = Field(..., min_length=1, max_length=100, description="ユーザー名")
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, description="パスワード（8文字以上）")
    # role はデフォルト "user" に自動設定

# ========== ユーザー更新時スキーマ ==========
class UserUpdate(BaseModel):
    """ユーザー更新リクエスト（すべて Optional）"""
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)  # 注：パスワード変更時のみ
    role: Optional[str] = None  # 注：管理者のみ変更可能

# ========== ユーザーレスポンススキーマ ==========
class UserResponse(BaseModel):
    """ユーザー取得時レスポンス（パスワードは含めない！）"""
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy ORM オブジェクト対応

# ========== ログインリクエストスキーマ ==========
class LoginRequest(BaseModel):
    """ログインリクエスト"""
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., description="パスワード")

# ========== トークンレスポンススキーマ ==========
class TokenResponse(BaseModel):
    """ログイン成功時レスポンス"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ========== トークンペイロード（内部用） ==========
class TokenPayload(BaseModel):
    """JWT トークン内部ペイロード"""
    user_id: int
    email: str
    role: str
    exp: int  # 有効期限（Unix Timestamp）