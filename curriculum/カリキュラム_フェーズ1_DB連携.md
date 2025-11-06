# FastAPI × PostgreSQL データベース連携 カリキュラム

## 学習目標
- PostgreSQLをDocker経由で構築
- SQLAlchemy ORMの基本を理解
- FastAPIでCRUD（Create, Read, Update, Delete）操作を実装
- 実務で使えるパターンを習得

---

## フェーズ1: 環境構築（PostgreSQL + SQLAlchemy）

### 目標
- docker-composeでPostgreSQLコンテナを追加
- FastAPIコンテナから接続確認
- 必要なPythonライブラリをインストール

### 必要なファイル修正
1. `requirements.txt`にSQLAlchemy関連を追加
2. `docker-compose.yml`にPostgreSQLサービスを追加
3. `database.py`を新規作成（DB接続設定）

### 学習ポイント
- PostgreSQLコンテナのヘルスチェック
- 環境変数によるDB接続設定
- SQLAlchemy エンジンの初期化

---

## フェーズ2: データモデル設計

### 目標
- テーブルスキーマを設計
- SQLAlchemy ORM モデルを定義
- マイグレーション基盤を用意

### 実装例：ユーザー管理テーブル
```
users テーブル
├── id (Primary Key)
├── name (文字列)
├── email (メールアドレス)
└── created_at (作成日時)
```

### 学習ポイント
- SQLAlchemy宣言的ベースの使用方法
- データ型の選択（String, Integer, DateTime等）
- 制約条件（NOT NULL, UNIQUE等）
- リレーション設計の基本

---

## フェーズ3: CRUD エンドポイント実装

### 3-1. **Create（作成）** - POST /users

**リクエスト例：**
```json
{
  "name": "山田太郎",
  "email": "yamada@example.com"
}
```

**レスポンス例（201 Created）：**
```json
{
  "id": 1,
  "name": "山田太郎",
  "email": "yamada@example.com",
  "created_at": "2025-11-05T12:34:56"
}
```

**実装ポイント：**
- Pydantic スキーマで入力バリデーション
- トランザクション処理
- 重複チェック（emailユニーク）
- 201ステータスコードの返却

---

### 3-2. **Read（読み取り）** - GET /users

#### 全件取得 - GET /users

**レスポンス例（200 OK）：**
```json
[
  {
    "id": 1,
    "name": "山田太郎",
    "email": "yamada@example.com",
    "created_at": "2025-11-05T12:34:56"
  },
  {
    "id": 2,
    "name": "佐藤花子",
    "email": "sato@example.com",
    "created_at": "2025-11-05T13:00:00"
  }
]
```

**実装ポイント：**
- ページネーション機能（オプション）
- 並べ替え機能

#### 個別取得 - GET /users/{id}

**レスポンス例（200 OK）：**
```json
{
  "id": 1,
  "name": "山田太郎",
  "email": "yamada@example.com",
  "created_at": "2025-11-05T12:34:56"
}
```

**実装ポイント：**
- 404エラーハンドリング（データ存在しない場合）
- パスパラメータのバリデーション

---

### 3-3. **Update（更新）** - PUT /users/{id}

**リクエスト例：**
```json
{
  "name": "山田次郎",
  "email": "yamada.jiro@example.com"
}
```

**レスポンス例（200 OK）：**
```json
{
  "id": 1,
  "name": "山田次郎",
  "email": "yamada.jiro@example.com",
  "created_at": "2025-11-05T12:34:56"
}
```

**実装ポイント：**
- 部分更新（必須フィールドのみ更新）
- 404エラーハンドリング
- バージョニング（楽観的ロック）- 応用

---

### 3-4. **Delete（削除）** - DELETE /users/{id}

**レスポンス例（204 No Content）：**
```
（ボディなし）
```

**実装ポイント：**
- 論理削除 vs 物理削除
- 404エラーハンドリング
- 204ステータスコードの返却

---

## フェーズ4: エラーハンドリング & バリデーション

### 目標
- 適切なHTTPステータスコードを返す
- 意味のあるエラーメッセージ
- データベース制約エラーの処理

### 実装するエラーパターン
| ステータス | 状況 | 例 |
|-----------|------|-----|
| 400 Bad Request | 入力形式エラー | メール形式が違う |
| 404 Not Found | リソース不在 | IDが見つからない |
| 409 Conflict | 重複制約違反 | メールアドレスが既に存在 |
| 500 Internal Server Error | DB接続エラー等 | 予期しないエラー |

### 学習ポイント
- FastAPI の HTTPException
- カスタム例外ハンドラ
- ログ出力

---

## フェーズ5: テスト（基礎）

### 目標
- ユニットテストの基本
- 各エンドポイントの動作確認
- エッジケースのテスト

### テスト項目例
```
[Create]
✓ 正常系：ユーザー作成成功
✓ 異常系：メール重複エラー
✓ 異常系：メール形式エラー

[Read]
✓ 正常系：全件取得
✓ 正常系：個別取得
✓ 異常系：存在しないID

[Update]
✓ 正常系：ユーザー更新成功
✓ 異常系：存在しないID

[Delete]
✓ 正常系：ユーザー削除成功
✓ 異常系：存在しないID
```

---

## 実装時の注意点

### セキュリティ
- パスワードは平文で保存しない（bcryptで暗号化）
- SQLインジェクション対策（SQLAlchemy ORM使用で自動対応）
- 入力値の厳密なバリデーション

### パフォーマンス
- N+1問題の回避（eagerロード）
- インデックス設定（emailカラム等）
- コネクションプール管理

### 保守性
- モデル層とビジネスロジック層の分離
- 命名規則の統一
- ドキュメント整備

---

## 推奨実装順序

1. **最小構成で動かす**
   - ユーザー作成（POST）1個
   - ユーザー一覧（GET）1個

2. **基本的なCRUDを完成**
   - Create, Read, Update, Delete

3. **エラーハンドリング強化**
   - 404, 409エラー対応

4. **テスト追加**
   - 正常系と異常系

5. **発展機能**（余裕があれば）
   - ページネーション
   - フィルタリング
   - ソート

---

## よくある質問・つまずき

### Q1: PostgreSQLに接続できない
**A:** docker-compose.ymlのポート設定とホスト名を確認してください
- コンテナ内: `postgresql://postgres:password@db:5432/fastapi_db`
- ホスト側: `postgresql://postgres:password@localhost:5432/fastapi_db`

### Q2: テーブルが自動作成されない
**A:** `Base.metadata.create_all(bind=engine)`を初回起動時に実行してください

### Q3: マイグレーション管理がしたい
**A:** Alembicライブラリを導入することで、バージョン管理が可能です（応用範囲）

---

## 次のステップ

このフェーズを完了したら：

- ✅ **認証・認可の実装**（JWT, ユーザーロール）
- ✅ **リレーション管理**（1対多、多対多）
- ✅ **マイグレーション自動化**（Alembic）
- ✅ **本番環境対応**（コネクションプール最適化など）

---

## 参考資料

- [SQLAlchemy 公式ドキュメント](https://docs.sqlalchemy.org/)
- [FastAPI データベース連携](https://fastapi.tiangolo.com/ja/tutorial/sql-databases/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)

---

作成日: 2025-11-05
