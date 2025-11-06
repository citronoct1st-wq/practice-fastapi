# FastAPI × PostgreSQL フェーズ3 CRUD エンドポイント実装 カリキュラム

## フェーズ3の目標

✅ CRUD エンドポイント（Create, Read, Update, Delete）の実装
✅ HTTPステータスコードの正しい使い分け
✅ エラーハンドリング（404, 409 Conflict など）
✅ リクエスト・レスポンスのバリデーション
✅ トランザクション処理の理解

---

## 学習内容の流れ

```
フェーズ2完了（テーブル・スキーマ定義）
        ↓
フェーズ3 ← 今ここ
├─ Step 0: ファイル構成設計（routers フォルダ作成）
├─ Step 1: API設計（エンドポイント仕様設計）
├─ Step 2: CREATE エンドポイント実装（POST /users）
├─ Step 3: READ エンドポイント実装（GET /users, GET /users/{id}）
├─ Step 4: UPDATE エンドポイント実装（PUT /users/{id}）
├─ Step 5: DELETE エンドポイント実装（DELETE /users/{id}）
└─ Step 6: 動作確認（Swagger UI / Thunder Client）
        ↓
フェーズ4: 認証・認可とセキュリティ
```

---

## Step 0: ファイル構成設計（routes フォルダ作成）

### 目的

実践的なプロジェクト構成を実現するため、エンドポイントをルータに分割します。

### ファイル構成

```
practice-fastapi/
├── Dockerfile
├── compose.yml
├── requirements.txt
├── main.py                          ← アプリケーション初期化のみ
├── database.py                      （変更なし）
├── models.py                        （変更なし）
├── schemas.py                       （変更なし）
├── routers/                         ← 新規フォルダ
│   ├── __init__.py                 （空ファイル）
│   └── users.py                    ← ユーザー関連エンドポイント
└── .gitignore
```

### フォルダ分割の利点

| 利点 | 説明 |
|------|------|
| **保守性向上** | ファイルが整理され、機能ごとに管理しやすい |
| **スケーラビリティ** | 新機能追加時に新ファイルを作成するだけ |
| **チームワーク** | チーム開発で役割分担しやすい |
| **テストケース** | ユニットテスト対象ごとにファイル分割可能 |

---

## Step 0-1: routers フォルダ作成と初期設定

### フォルダ構成ファイル

**routers/__init__.py** を新規作成（内容は空でOK）：

```python
# routers/__init__.py
# パッケージ化するための空ファイル
```

**routers/users.py** を新規作成：

```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserUpdate

# APIRouter を作成（FastAPI アプリケーションの一部）
router = APIRouter(
    prefix="/users",           # エンドポイント前置詞
    tags=["users"]             # Swagger UI で分類
)

# ここにエンドポイント実装（Step 2-5 で追加）
```

### APIRouter の説明

```python
router = APIRouter(prefix="/users", tags=["users"])
```

| 設定 | 説明 |
|------|------|
| `prefix="/users"` | すべてのエンドポイントに `/users` を自動付与 |
| `tags=["users"]` | Swagger UI で「users」カテゴリに分類 |

**例:**
```python
@router.post("")  # 実際のエンドポイントは POST /users
def create_user(...):
    pass

@router.get("/{user_id}")  # 実際のエンドポイントは GET /users/{user_id}
def read_user(...):
    pass
```

---

## Step 0-2: main.py をシンプルに修正

**修正前の main.py:**
```python
# main.py（修正前）
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import engine, Base, get_db, SessionLocal
from models import User
from schemas import UserCreate, UserResponse, UserUpdate
from sqlalchemy import text

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/users", ...)  # ← エンドポイント実装が長くなる
def create_user(...):
    pass

# ... その他のエンドポイント
```

**修正後の main.py（推奨）:**
```python
from fastapi import FastAPI
from database import engine, Base, SessionLocal
from sqlalchemy import text
from routers import users  # ← ルータをインポート

# テーブル自動生成
Base.metadata.create_all(bind=engine)

# FastAPI アプリケーション作成
app = FastAPI(
    title="User Management API",
    description="ユーザー管理API",
    version="1.0.0"
)

# ルータを登録（エンドポイントを組み込む）
app.include_router(users.router)

# DB接続確認（起動時実行）
@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        print("✓ Database connected successfully!")
    finally:
        db.close()
```

### main.py の責務

修正後の `main.py` は以下の責務のみを持つ：

1. FastAPI アプリケーション作成
2. テーブル自動生成
3. ルータ登録
4. グローバル設定（CORS等）
5. 起動時処理

**利点:**
- ファイルが短く読みやすい
- 全体構成が一目瞭然
- エンドポイント実装と分離

---

## Step 0-3: Dockerfile 修正確認

routers フォルダが追加されたため、Dockerfile は修正不要です。

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY database.py .
COPY models.py .
COPY schemas.py .
# COPY routers/ routers/  ← ディレクトリ全体をコピー（または以下を個別に記述）
COPY routers .  # ← routers フォルダ全体をコピー

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**確認ポイント:**
```dockerfile
COPY routers .  # ← routers フォルダ全体をコピーしているか確認
```

---

## Step 1: API設計（エンドポイント仕様設計）

### 目的

ユーザー管理 API の全体設計を理解します。

### エンドポイント一覧

| HTTPメソッド | エンドポイント | 説明 | ステータス |
|------------|--------------|------|---------|
| `POST` | `/users` | ユーザー作成 | 201 Created |
| `GET` | `/users` | 全ユーザー取得 | 200 OK |
| `GET` | `/users/{id}` | 特定ユーザー取得 | 200 OK |
| `PUT` | `/users/{id}` | ユーザー更新 | 200 OK |
| `DELETE` | `/users/{id}` | ユーザー削除 | 204 No Content |

### 各エンドポイントの詳細仕様

#### 1. POST /users（ユーザー作成）

**リクエストボディ:**
```json
{
  "name": "山田太郎",
  "email": "yamada@example.com"
}
```

**成功時レスポンス（201 Created）:**
```json
{
  "id": 1,
  "name": "山田太郎",
  "email": "yamada@example.com",
  "created_at": "2025-11-06T12:00:00"
}
```

**エラーレスポンス例（409 Conflict）:**
```json
{
  "detail": "メールアドレスは既に登録されています"
}
```

**バリデーションルール:**
- `name`: 必須、文字列
- `email`: 必須、有効なメール形式

---

#### 2. GET /users（全ユーザー取得）

**リクエスト:** パラメータなし

**成功時レスポンス（200 OK）:**
```json
[
  {
    "id": 1,
    "name": "山田太郎",
    "email": "yamada@example.com",
    "created_at": "2025-11-06T12:00:00"
  },
  {
    "id": 2,
    "name": "田中花子",
    "email": "tanaka@example.com",
    "created_at": "2025-11-06T12:05:00"
  }
]
```

---

#### 3. GET /users/{id}（特定ユーザー取得）

**リクエスト:** `id` はパスパラメータ（整数）

**成功時レスポンス（200 OK）:**
```json
{
  "id": 1,
  "name": "山田太郎",
  "email": "yamada@example.com",
  "created_at": "2025-11-06T12:00:00"
}
```

**エラーレスポンス例（404 Not Found）:**
```json
{
  "detail": "ユーザーが見つかりません"
}
```

---

#### 4. PUT /users/{id}（ユーザー更新）

**リクエスト:**
```json
{
  "name": "山田次郎",
  "email": "yamada.jiro@example.com"
}
```

**成功時レスポンス（200 OK）:**
```json
{
  "id": 1,
  "name": "山田次郎",
  "email": "yamada.jiro@example.com",
  "created_at": "2025-11-06T12:00:00"
}
```

**エラーケース:**
- 404 Not Found: ユーザーが存在しない
- 409 Conflict: 新しいメールが既に登録済み

**更新ルール:**
- 両フィールドが Optional（任意）
- 最低1つは指定が必須

---

#### 5. DELETE /users/{id}（ユーザー削除）

**リクエスト:** `id` はパスパラメータ（整数）

**成功時レスポンス（204 No Content）:**
```
レスポンスボディなし
```

**エラーレスポンス例（404 Not Found）:**
```json
{
  "detail": "ユーザーが見つかりません"
}
```

---

## HTTPステータスコード解説

### 使用するステータスコード一覧

| コード | 意味 | 使用場面 |
|-------|------|--------|
| `200` | OK | 取得・更新成功 |
| `201` | Created | 新規作成成功 |
| `204` | No Content | 削除成功（レスポンスボディなし） |
| `400` | Bad Request | リクエスト形式エラー（バリデーション失敗） |
| `404` | Not Found | リソース未検出 |
| `409` | Conflict | リソース競合（重複エラー等） |
| `500` | Internal Server Error | サーバーエラー |

**FastAPI での設定例:**
```python
@app.post("/users", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 201 で返却される
    pass
```

---

## Step 2: CREATE エンドポイント実装（POST /users）

### 目的

新しいユーザーを作成するエンドポイントを実装します。

### 実装コード

**routers/users.py に以下を追加：**

```python
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
```

### 各要素の解説

#### デコレータと設定

```python
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
```

| 設定 | 説明 |
|------|------|
| `@app.post("/users")` | POST メソッド、エンドポイント `/users` |
| `response_model=UserResponse` | レスポンスをこのスキーマで変換・バリデーション |
| `status_code=201` | 成功時のHTTPステータス（201 Created） |
| `user: UserCreate` | リクエストボディを自動バリデーション |
| `db: Session = Depends(get_db)` | 依存性注入。DB セッション自動取得 |

#### トランザクション処理

```python
db.add(db_user)        # Add フェーズ：準備
db.commit()            # Commit フェーズ：反映
db.refresh(db_user)    # Refresh フェーズ：再取得
```

**フロー図:**

```
1. db.add()
   ↓
   メモリ上に User オブジェクト追加
   ↓
2. db.commit()
   ↓
   INSERT文を実行
   トランザクション確定
   ↓
3. db.refresh()
   ↓
   DB から最新データを再取得
   id, created_at 等が自動設定された値を取得
   ↓
レスポンス返却
```

#### エラーハンドリング

```python
except IntegrityError:
    db.rollback()
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="メールアドレスは既に登録されています"
    )
```

**IntegrityError が発生する場合:**
- `email` の UNIQUE 制約違反
- `name` または `email` が NOT NULL なのに NULL が入った

**db.rollback() の役割:**
- トランザクションを取り消し
- 部分的な更新を防ぐ

---

## Step 3: READ エンドポイント実装（GET /users, GET /users/{id}）

### 全ユーザー取得（GET /users）

**routers/users.py に以下を追加：**

```python
@router.get("", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db)):
    """全ユーザー取得エンドポイント

    Returns:
        list[UserResponse]: ユーザー情報のリスト
    """
    users = db.query(User).all()
    return users
```

**コード解説:**

```python
db.query(User).all()
```

| メソッド | 説明 |
|---------|------|
| `db.query(User)` | User テーブルに対するクエリビルダを作成 |
| `.all()` | すべてのレコードを取得してリストで返す |

**生成されるSQL:**
```sql
SELECT * FROM users;
```

**レスポンス例:**
```json
[
  {
    "id": 1,
    "name": "山田太郎",
    "email": "yamada@example.com",
    "created_at": "2025-11-06T12:00:00"
  }
]
```

---

### 特定ユーザー取得（GET /users/{id}）

**routers/users.py に以下を追加：**

```python
@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """特定ユーザー取得エンドポイント

    Args:
        user_id: ユーザーID（パスパラメータ）
        db: データベースセッション

    Returns:
        UserResponse: ユーザー情報

    Raises:
        HTTPException 404: ユーザーが見つからない
    """
    # IDで検索
    db_user = db.query(User).filter(User.id == user_id).first()

    # ユーザーが存在しない場合はエラー
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )

    return db_user
```

**コード解説:**

```python
db.query(User).filter(User.id == user_id).first()
```

| メソッド | 説明 |
|---------|------|
| `db.query(User)` | User テーブルをクエリ |
| `.filter(User.id == user_id)` | WHERE条件を追加 |
| `.first()` | 最初の1件を取得（ない場合は None） |

**生成されるSQL:**
```sql
SELECT * FROM users WHERE id = 1 LIMIT 1;
```

**エラーハンドリング:**

```python
if not db_user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="ユーザーが見つかりません"
    )
```

**HTTPException の動作:**
- FastAPI が自動的に JSON エラーレスポンスを生成
- `status_code`: HTTPステータスコード
- `detail`: エラーメッセージ

**エラーレスポンス例:**
```json
{
  "detail": "ユーザーが見つかりません"
}
```

---

## Step 4: UPDATE エンドポイント実装（PUT /users/{id}）

### 実装コード

**routers/users.py に以下を追加：**

```python
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """ユーザー更新エンドポイント

    Args:
        user_id: ユーザーID（パスパラメータ）
        user_update: 更新内容（name, email は任意）
        db: データベースセッション

    Returns:
        UserResponse: 更新されたユーザー情報

    Raises:
        HTTPException 404: ユーザーが見つからない
        HTTPException 409: 新しいメールが既に登録されている
    """
    # 対象ユーザーを取得
    db_user = db.query(User).filter(User.id == user_id).first()

    # ユーザーが存在しない場合はエラー
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
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
```

### 各要素の解説

#### Optional フィールドの処理

```python
if user_update.name is not None:
    db_user.name = user_update.name
```

**重要:**
- `UserUpdate` スキーマで `Optional` を使用
- `None` チェックで更新フィールドのみ反映
- 提供されないフィールドは変更しない

**リクエスト例1（名前のみ更新）:**
```json
{
  "name": "山田次郎"
}
```

**DB反映後:**
```
id=1
name=山田次郎  （更新）
email=yamada@example.com  （変更なし）
```

#### UNIQUE 制約エラーハンドリング

```python
except IntegrityError:
    db.rollback()
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="メールアドレスは既に登録されています"
    )
```

**409 Conflict を使用する理由:**
- リソース競合を意味する
- メール重複は「競合」扱い

---

## Step 5: DELETE エンドポイント実装（DELETE /users/{id}）

### 実装コード

**routers/users.py に以下を追加：**

```python
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザー削除エンドポイント

    Args:
        user_id: ユーザーID（パスパラメータ）
        db: データベースセッション

    Raises:
        HTTPException 404: ユーザーが見つからない
    """
    # 対象ユーザーを取得
    db_user = db.query(User).filter(User.id == user_id).first()

    # ユーザーが存在しない場合はエラー
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )

    # データベースから削除
    db.delete(db_user)

    # コミット（実際に反映）
    db.commit()

    # 204 No Content なのでレスポンスボディは返さない
```

### 各要素の解説

#### 204 No Content ステータス

```python
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
```

**特徴:**
- 削除成功時に `204` を返す
- レスポンスボディは返さない（`response_model` を指定しない）
- ブラウザやクライアントに削除完了を知らせる

**RESTful API の慣例:**
- POST（作成）→ 201 Created + ボディ
- PUT（更新）→ 200 OK + ボディ
- DELETE（削除）→ 204 No Content（ボディなし）

#### DELETE SQL生成

```python
db.delete(db_user)
db.commit()
```

**生成されるSQL:**
```sql
DELETE FROM users WHERE id = 1;
```

---

## Step 6: 動作確認

### チェックリスト

- [ ] `routers` フォルダ作成
- [ ] `routers/__init__.py` を作成（空ファイル）
- [ ] `routers/users.py` を作成（APIRouter + 5つのエンドポイント実装）
- [ ] `main.py` を修正（アプリケーション初期化 + `include_router(users.router)` 追加）
- [ ] Dockerfile に `COPY routers .` を追加
- [ ] インポート文を確認（APIRouter, HTTPException, status 等）
- [ ] `docker-compose down && docker-compose up --build` 実行
- [ ] FastAPI起動ログに「Application startup complete」が表示されるか確認
- [ ] `http://localhost:8000/docs` で Swagger UI にアクセス

### Swagger UI での動作確認

#### 1. ユーザー作成（POST /users）

1. Swagger UI を開く: `http://localhost:8000/docs`
2. `/users` の POST をクリック
3. 「Try it out」をクリック
4. RequestBody に以下を入力：
```json
{
  "name": "山田太郎",
  "email": "yamada@example.com"
}
```
5. 「Execute」をクリック
6. **期待される結果**: 201 Created + ユーザー情報がレスポンス

#### 2. 全ユーザー取得（GET /users）

1. `/users` の GET をクリック
2. 「Try it out」→「Execute」をクリック
3. **期待される結果**: 200 OK + ユーザーのリストが返ってくる

#### 3. 特定ユーザー取得（GET /users/{id}）

1. `/users/{user_id}` の GET をクリック
2. 「Try it out」をクリック
3. `user_id` に `1` を入力
4. 「Execute」をクリック
5. **期待される結果**: 200 OK + ユーザー情報（id=1）が返ってくる

#### 4. ユーザー更新（PUT /users/{id}）

1. `/users/{user_id}` の PUT をクリック
2. 「Try it out」をクリック
3. `user_id` に `1` を入力
4. RequestBody に以下を入力：
```json
{
  "name": "山田次郎"
}
```
5. 「Execute」をクリック
6. **期待される結果**: 200 OK + 更新されたユーザー情報

#### 5. ユーザー削除（DELETE /users/{id}）

1. `/users/{user_id}` の DELETE をクリック
2. 「Try it out」をクリック
3. `user_id` に `1` を入力
4. 「Execute」をクリック
5. **期待される結果**: 204 No Content（レスポンスボディなし）

### Thunder Client での動作確認（代替方法）

Swagger UI の代わりに Thunder Client（VS Code拡張）を使用できます。

**インストール:**
1. VS Code 拡張マーケットプレイスで「Thunder Client」検索
2. インストール
3. VS Code 左バーのアイコンをクリック

**リクエスト例:**
```
POST http://localhost:8000/users
Content-Type: application/json

{
  "name": "山田太郎",
  "email": "yamada@example.com"
}
```

---

## よくあるエラーと対応

### エラー1: "detail": "Unprocessable Entity"（422）

**原因:** リクエストボディのバリデーション失敗

**例:**
```json
{
  "name": "山田太郎",
  "email": "invalid-email"  // ❌ メール形式ではない
}
```

**解決:**
- メールアドレス形式を確認
- リクエストボディのJSON形式を確認

### エラー2: "detail": "メールアドレスは既に登録されています"（409）

**原因:** 同じメールアドレスで複数ユーザーを作成しようとした

**解決:**
```bash
# テーブルをリセット（開発環境のみ）
docker-compose exec db psql -U postgres -d fastapi_db
# psql> DROP TABLE users;
# psql> \q
docker-compose restart fastapi
```

### エラー3: "detail": "ユーザーが見つかりません"（404）

**原因:** 存在しないユーザーIDで取得・更新・削除しようとした

**解決:**
1. 先に POST /users でユーザー作成
2. 返された `id` を確認
3. その ID で GET / PUT / DELETE を実行

### エラー4: "IntegrityError" または "UNIQUE constraint failed"

**原因:** トランザクション中の制約違反

**ログ例:**
```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint
```

**解決:**
- エラーハンドリングコードが正しく実装されているか確認
- `IntegrityError` の `except` ブロックが実行されているか確認

---

## ファイル構成確認（フェーズ3完了時）

```
practice-fastapi/
├── Dockerfile                              ← COPY routers . 追加
├── compose.yml                             （変更なし）
├── requirements.txt                        （変更なし）
├── main.py                                 ← シンプルに修正
├── database.py                             （変更なし）
├── models.py                               （変更なし）
├── schemas.py                              （変更なし）
├── routers/                                ← 新規フォルダ
│   ├── __init__.py                        ← 新規（空ファイル）
│   └── users.py                           ← 新規（5つのエンドポイント）
├── .gitignore
├── 学習メモ.md
├── curriculum/
│   ├── カリキュラム_フェーズ1_DB連携.md
│   ├── カリキュラム_フェーズ2_データモデル設計.md
│   └── カリキュラム_フェーズ3_CRUD実装.md      ← 本ファイル
├── studymemo/
│   ├── 学習メモ_フェーズ1完了.md
│   └── 学習メモ_フェーズ2完了.md
```

### ファイル修正内容

#### 1. Dockerfile（修正）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY database.py .
COPY models.py .
COPY schemas.py .
COPY routers .          # ← routers フォルダを追加

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. main.py（修正・シンプル化）

```python
from fastapi import FastAPI
from database import engine, Base, SessionLocal
from sqlalchemy import text
from routers import users

# テーブル自動生成
Base.metadata.create_all(bind=engine)

# FastAPI アプリケーション作成
app = FastAPI(
    title="User Management API",
    description="ユーザー管理API",
    version="1.0.0"
)

# ルータを登録
app.include_router(users.router)

# DB接続確認（起動時実行）
@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        print("✓ Database connected successfully!")
    finally:
        db.close()
```

#### 3. routers/__init__.py（新規・空ファイル）

```python
# routers/__init__.py
# パッケージ化するための空ファイル
```

#### 4. routers/users.py（新規・5つのエンドポイント）

```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

# Step 2: CREATE - POST /users
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # ... 実装（Step 2参照）

# Step 3: READ - GET /users
@router.get("", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db)):
    # ... 実装（Step 3参照）

# Step 3: READ - GET /users/{user_id}
@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    # ... 実装（Step 3参照）

# Step 4: UPDATE - PUT /users/{user_id}
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    # ... 実装（Step 4参照）

# Step 5: DELETE - DELETE /users/{user_id}
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # ... 実装（Step 5参照）
```

### 実装のポイント

| ファイル | ポイント |
|---------|---------|
| `main.py` | アプリケーション初期化のみ。エンドポイントなし |
| `routers/users.py` | APIRouter でエンドポイント実装。`@router` デコレータを使用 |
| `routers/__init__.py` | 空ファイル。Python でフォルダをパッケージ化 |

---

## RESTful API 設計の原則

### HTTP メソッドの使い分け

| メソッド | 用途 | べき等性 | キャッシング |
|---------|------|--------|----------|
| `GET` | データ取得 | ✅ | ✅ |
| `POST` | リソース作成 | ❌ | ❌ |
| `PUT` | リソース置換 | ✅ | ❌ |
| `DELETE` | リソース削除 | ✅ | ❌ |
| `PATCH` | 部分更新 | ❌ | ❌ |

**べき等性とは:**
- 同じ操作を何度実行しても結果が変わらない性質
- `GET` x10回 = `GET` x1回（べき等）
- `POST` x10回 ≠ `POST` x1回（べき等でない：10個作成される）

### ステータスコードの選択

```
1xx（100-199）  情報
2xx（200-299）  成功 ← 使用
3xx（300-399）  リダイレクト
4xx（400-499）  クライアントエラー ← 使用
5xx（500-599）  サーバーエラー
```

**フェーズ3で使用:**
- 201 Created：リソース作成成功
- 200 OK：取得・更新成功
- 204 No Content：削除成功
- 404 Not Found：リソース未検出
- 409 Conflict：リソース競合

---

## 学習のコツ

✅ **小さく試す**
- 最初は CREATE だけ動作確認
- 次に READ、順に実装
- 大きな機能を一気に実装しない

✅ **ログを活用**
```bash
docker-compose logs fastapi
```
- エラーメッセージを読む
- `print()` で値を確認

✅ **Swagger UI を活用**
- `http://localhost:8000/docs`
- 自動生成 API ドキュメント
- インタラクティブに動作確認

✅ **DB状態を確認**
```bash
docker-compose exec db psql -U postgres -d fastapi_db -c "SELECT * FROM users;"
```
- 実際の DB データを確認
- API の動作を DB 側から検証

✅ **HTTPステータスコードを理解**
- 2xx：成功
- 4xx：クライアント側の問題
- 5xx：サーバー側の問題

---

## 推奨スケジュール

**Day 1（フェーズ3初日）:**
- Step 0: ファイル構成設計（routers フォルダ作成、main.py 修正）
- Step 1: API設計の理解
- Step 2: CREATE 実装 + 動作確認
- 合計時間: 45-60分

**Day 2（フェーズ3中日）:**
- Step 3: READ 実装 + 動作確認
- 合計時間: 30-40分

**Day 3（フェーズ3完了日）:**
- Step 4-5: UPDATE / DELETE 実装
- Step 6: 全体動作確認
- 合計時間: 40-50分

---

## 完了の確認

フェーズ3 完了条件（すべて ✅ か確認）：

**ファイル構成:**
- [ ] `routers` フォルダを作成
- [ ] `routers/__init__.py` を作成（空ファイル）
- [ ] `routers/users.py` を作成

**routers/users.py の実装:**
- [ ] `APIRouter` を定義（`prefix="/users"`, `tags=["users"]`）
- [ ] 5つのエンドポイント実装（POST, GET x2, PUT, DELETE）
- [ ] `@router` デコレータを使用（`@app` ではなく）
- [ ] `HTTPException`, `status` をインポート
- [ ] エラーハンドリング（404, 409）を実装
- [ ] `IntegrityError` をハンドリング

**main.py の修正:**
- [ ] `routers` から `users` をインポート
- [ ] `app.include_router(users.router)` で登録
- [ ] アプリケーション初期化のみ（エンドポイントなし）

**Dockerfile の修正:**
- [ ] `COPY routers .` を追加

**動作確認:**
- [ ] `docker-compose up --build` が成功
- [ ] FastAPI起動ログに「✓ Database connected successfully!」が表示
- [ ] Swagger UI `/docs` にアクセス可能
- [ ] POST /users でユーザー作成可能（201返却）
- [ ] GET /users で全ユーザー取得可能（200返却）
- [ ] GET /users/{id} で特定ユーザー取得可能（200返却、存在しないIDで404）
- [ ] PUT /users/{id} でユーザー更新可能（200返却）
- [ ] DELETE /users/{id} でユーザー削除可能（204返却）

**すべての項目が ✅ であれば、フェーズ3 完了！**

---

## 次のステップ（フェーズ4の予告）

フェーズ4では以下を実装します：

- パスワード認証機能
- JWT トークン発行・検証
- ロールベースアクセス制御（RBAC）
- セキュアなデータベース操作

---

## 参考リンク

- FastAPI 公式: https://fastapi.tiangolo.com/
- SQLAlchemy 公式: https://docs.sqlalchemy.org/
- HTTP ステータスコード: https://developer.mozilla.org/ja/docs/Web/HTTP/Status

---

頑張ってください！
