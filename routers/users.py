from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """ユーザー作成エンドポイント

    Args:
        user: ユーザー作成用スキーマ（name, email）
        db: データベースセッション（自動注入）

    Returns:
        UserResponse: 作成されたユーザー情報

    Raises:
        HTTPException 409: メールアドレスが既に登録されている
    """
    try:
        # 新規 User オブジェクト作成
        db_user = User(name=user.name, email=user.email)

        # データベースに追加（トランザクション開始）
        db.add(db_user)

        # コミット（実際にDB反映）
        db.commit()

        # 作成されたレコードを再取得（id, created_at 等が反映される）
        db.refresh(db_user)

        return db_user

    except IntegrityError:
        # トランザクション状態をリセット
        db.rollback()

        # クライアントにエラー返却（409 Conflict）
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="メールアドレスは既に登録されています"
        )
    
@router.get("", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db)):
    """全ユーザー取得エンドポイント

    Returns:
        list[UserResponse]: ユーザ情報のリスト
    """
    users = db.query(User).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """特定ユーザ取得エンドポイント

    Args:
        user_id: ユーザID（パスパラメータ）
        db: データベースセッション

    Returns:
        UserResponse: ユーザ情報
    
    Raises:
        HTTPException 404: ユーザが見つからない
    """
    # IDで検索
    db_user = db.query(User).filter(User.id == user_id).first()

    #ユーザが存在しない場合はエラー
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザが見つかりません"
        )
    
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """ユーザ更新エンドポイント

    Args:
        user_id: ユーザID（パスパラメータ）
        user_update: 更新内容(name, email は任意)
        db: データベースセッション

    Returns:
        UserResponse: 更新されたユーザ情報

    Raises:
        HTTPException 404: ユーザが見つからない
        HTTPException 409: 新しいメールが既に登録されている
    """
    # 対象ユーザを取得
    db_user = db.query(User).filter(User.id == user_id).first()

    # ユーザが存在しない場合はエラー
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザが見つかりません"
        )
    
    try:
        # 更新フィールドのみ反映（None 以外）
        if user_update.name is not None:
            db_user.name = user_update.name

        if user_update.email is not None:
            db_user.email = user_update.email

        # コミット
        db.commit()

        # 更新後のデータを再取得
        db.refresh(db_user)

        return db_user
    
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="メールアドレスは既に登録されています"
        )
    
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザ削除エンドポイント
    
    Args:
        user_id: ユーザID（パスパラメータ）
        db: データベースセッション

    Raises:
        HTTPException 404: ユーザが見つからない
    """
    # 対象ユーザを取得
    db_user = db.query(User).filter(User.id == user_id).first()

    # ユーザが存在しない場合エラー
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザが見つかりません"
        )
    
    # データベースから削除
    db.delete(db_user)

    # コミット
    db.commit()

    # 204 No Content なのでレスポンスボディは返さない