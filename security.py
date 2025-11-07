from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from schemas import TokenPayload
from database import get_db
from models import User

# ========== パスワード暗号化設定 ==========
pwd_context = CryptContext(
    schemes=["bcrypt"],           # bcrypt を使用
    deprecated="auto"
)

# ========== JWT 設定 ==========
SECRET_KEY = "your-secret-key-change-in-production"  # ⚠️ 本番環境では環境変数から
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # トークン有効期限：60分

# ========== パスワード関連関数 ==========
def hash_password(password: str) -> str:
    """平文のパスワードをハッシング

    Args:
        password: 平文パスワード

    Returns:
        ハッシング化されたパスワード

    例:
        >>> hash_password("password123")
        '$2b$12$...'
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """平文パスワードがハッシュと一致するか検証

    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシング化されたパスワード

    Returns:
        bool: 一致すれば True、不一致なら False

    例:
        >>> hash_pw = hash_password("password123")
        >>> verify_password("password123", hash_pw)
        True
        >>> verify_password("wrong", hash_pw)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ========== JWT 関連関数 ==========
def create_access_token(
    user_id: int,
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """JWT トークンを生成

    Args:
        user_id: ユーザーID
        email: メールアドレス
        role: ロール（admin, user）
        expires_delta: トークン有効期限（デフォルト: 60分）

    Returns:
        JWT トークン文字列

    例:
        >>> token = create_access_token(user_id=1, email="user@example.com", role="user")
        >>> # トークンは以下の形式: eyJ...（JWT）
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": int(expire.timestamp())  # Unix Timestamp
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenPayload]:
    """JWT トークンを検証してペイロードを取得

    Args:
        token: JWT トークン文字列

    Returns:
        TokenPayload: トークンペイロード（無効なら None）

    例:
        >>> token = "eyJ..."
        >>> payload = verify_token(token)
        >>> if payload:
        ...     print(f"User ID: {payload.user_id}")
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except JWTError:
        return None


# ========== 認証ヘッダーからトークンを抽出 ==========
def _extract_token_from_header(authorization: str | None = Header(None)) -> str:
    """Authorization ヘッダーから Bearer トークンを抽出

    Args:
        authorization: Authorization ヘッダー（自動注入）

    Returns:
        str: トークン文字列

    Raises:
        HTTPException 401: Authorization ヘッダーがない、または形式が違う

    例:
        Authorization: Bearer eyJ...
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization ヘッダーが必要です",
            headers={"WWW-Authenticate": "Bearer"}
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効な Authorization ヘッダー形式です",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return parts[1]


# ========== 現在のユーザーを取得する依存性関数 ==========
def get_current_user(
    token: Annotated[str, Depends(_extract_token_from_header)],
    db: Session = Depends(get_db)
) -> User:
    """リクエストから現在のユーザーを取得

    Args:
        token: JWT トークン（Authorization ヘッダーから自動抽出）
        db: データベースセッション

    Returns:
        User: 認証済みユーザーオブジェクト

    Raises:
        HTTPException 401: トークンが無効または期限切れ

    例:
        @router.get("/profile")
        def get_profile(user: User = Depends(get_current_user)):
            return user
    """
    # トークンを検証
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # ユーザーを DB から取得
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つかりません",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """現在のユーザーが admin ロールであることを確認

    Args:
        current_user: 認証済みユーザー

    Returns:
        User: admin ロールのユーザー

    Raises:
        HTTPException 403: admin ロールではない

    例:
        @router.delete("/users/{user_id}")
        def delete_user(user_id: int, admin: User = Depends(get_current_admin)):
            # このエンドポイントは admin のみアクセス可能
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このオペレーションは管理者のみ実行可能です"
        )
    return current_user