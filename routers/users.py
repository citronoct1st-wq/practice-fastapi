from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse, UserCreate, UserResponse, UserUpdate
from security import hash_password, verify_password, create_access_token, get_current_user, get_current_admin

router = APIRouter(prefix="/users", tags=["users"])

# ========== ログインエンドポイント ==========
@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    """ユーザーログインエンドポイント（認証）

    Args:
        login_request: メールアドレスとパスワード
        db: データベースセッション

    Returns:
        TokenResponse: JWT トークンとユーザー情報

    Raises:
        HTTPException 401: メールアドレスまたはパスワードが間違っている

    リクエスト例:
        POST /users/login
        Content-Type: application/json

        {
          "email": "user@example.com",
          "password": "password123"
        }

    成功レスポンス（200 OK）:
        {
          "access_token": "eyJ...",
          "token_type": "bearer",
          "user": {
            "id": 1,
            "name": "山田太郎",
            "email": "yamada@example.com",
            "role": "user",
            "is_active": true,
            "created_at": "2025-11-06T12:00:00"
          }
        }
    """
    # メールアドレスで ユーザー検索
    user = db.query(User).filter(User.email == login_request.email).first()

    # ユーザーが存在しない、またはパスワード不一致
    if not user or not verify_password(login_request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが間違っています",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # ユーザーが無効化されている
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このユーザーアカウントは無効化されています"
        )

    # JWT トークンを生成
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# ========== ユーザー作成（新規ユーザー登録） ==========
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """新規ユーザー登録エンドポイント（認証不要）

    このエンドポイントは誰でもアクセス可能（認証不要）
    新規ユーザー登録用

    Args:
        user: ユーザー作成スキーマ（name, email, password）
        db: データベースセッション

    Returns:
        UserResponse: 作成されたユーザー情報

    Raises:
        HTTPException 409: メールアドレスが既に登録されている
    """
    try:
        # パスワードをハッシング
        hashed_password = hash_password(user.password)

        # 新規 User オブジェクト作成
        db_user = User(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password,
            role="user"  # 新規ユーザーはデフォルト "user" ロール
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="メールアドレスは既に登録されています"
        )

# ========== 自分のプロフィール取得 ==========
@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """認証済みユーザーの自分のプロフィール取得

    Args:
        current_user: 認証済みユーザー（自動注入）

    Returns:
        UserResponse: ユーザー情報

    使用例:
        GET /users/me
        Authorization: Bearer eyJ...
    """
    return current_user

# ========== 全ユーザー取得（管理者のみ） ==========
@router.get("", response_model=list[UserResponse])
def read_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """全ユーザー取得（admin ロールのみ）

    Args:
        admin: admin ロールの認証済みユーザー
        db: データベースセッション

    Returns:
        list[UserResponse]: 全ユーザーのリスト

    注意:
        admin ロールのトークンが必須
        user ロールでリクエストした場合は 403 Forbidden エラー
    """
    users = db.query(User).all()
    return users


# ========== 特定ユーザー取得 ==========
@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """特定ユーザー取得（認証必須、ユーザー本人またはadmin）

    Args:
        user_id: ユーザーID
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        UserResponse: ユーザー情報

    アクセス制御:
        - user ロール：自分のプロフィールのみ取得可能
        - admin ロール：全ユーザー取得可能

    Raises:
        HTTPException 403: アクセス権限なし
        HTTPException 404: ユーザーが見つからない
    """
    # ユーザーを DB から取得
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )

    # 権限チェック：user ロールは自分のみ、admin ロールは全員
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このユーザーのプロフィールを表示する権限がありません"
        )

    return db_user


# ========== ユーザー更新 ==========
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ユーザー更新（認証必須、ユーザー本人またはadmin）

    Args:
        user_id: ユーザーID
        user_update: 更新内容（name, email, password, role）
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        UserResponse: 更新されたユーザー情報

    制限事項:
        - user ロール：自分の name, email, password のみ変更可能
        - admin ロール：全フィールド変更可能

    Raises:
        HTTPException 403: 権限なし
        HTTPException 404: ユーザーが見つからない
        HTTPException 409: メール重複
    """
    # 対象ユーザーを取得
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )

    # 権限チェック：user ロールは自分のみ、admin ロールは全員
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このユーザーを編集する権限がありません"
        )

    # user ロールは role フィールドを変更できない
    if current_user.role != "admin" and user_update.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ロール変更は管理者のみ可能です"
        )

    try:
        # 更新フィールドを反映
        if user_update.name is not None:
            db_user.name = user_update.name

        if user_update.email is not None:
            db_user.email = user_update.email

        if user_update.password is not None:
            db_user.hashed_password = hash_password(user_update.password)

        # admin のみロール変更可能
        if user_update.role is not None and current_user.role == "admin":
            db_user.role = user_update.role

        db.commit()
        db.refresh(db_user)

        return db_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="メールアドレスは既に登録されています"
        )

# ========== ユーザー削除（管理者のみ） ==========
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ユーザー削除（admin ロールのみ）

    Args:
        user_id: ユーザーID
        admin: admin ロールの認証済みユーザー
        db: データベースセッション

    Raises:
        HTTPException 403: admin ロールではない
        HTTPException 404: ユーザーが見つからない

    注意:
        自分自身は削除できない
    """
    # 自分自身の削除を防ぐ
    if admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="自分自身を削除することはできません"
        )

    # 対象ユーザーを取得
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )

    # 削除
    db.delete(db_user)
    db.commit()


# ========== ユーザー作成（管理者専用：任意のロール指定可能） ==========
@router.post("/admin/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_by_admin(
    user: UserCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ユーザー作成エンドポイント（管理者専用）

    管理者のみが使用可能。通常ユーザーの作成と異なり、ロール指定は不可。
    通常は POST /users（新規ユーザー登録）を使用してください。

    Args:
        user: ユーザー作成スキーマ（name, email, password）
        admin: admin ロールの認証済みユーザー
        db: データベースセッション

    Returns:
        UserResponse: 作成されたユーザー情報

    Raises:
        HTTPException 403: admin ロールではない
        HTTPException 409: メールアドレスが既に登録されている

    注意:
        管理者が作成したユーザーも自動的に role="user" で作成されます。
        role を変更したい場合は PUT /users/{id} で更新してください。
    """
    try:
        # パスワードをハッシング
        hashed_password = hash_password(user.password)

        # 新規 User オブジェクト作成
        db_user = User(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password,
            role="user"  # 管理者が作成してもデフォルトは "user" ロール
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="メールアドレスは既に登録されています"
        )