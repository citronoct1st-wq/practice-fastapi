# FastAPI User Management API

学習目的で構築したユーザー管理APIのプロジェクトです。FastAPIとPostgreSQLを使用して、基本的なCRUD操作と認証機能を実装しています。

## 学習の目的

このプロジェクトは以下のスキル習得を目的としています。

- **FastAPI の基礎**: エンドポイント設計、依存性注入、リクエスト/レスポンス処理
- **データベース設計**: PostgreSQLテーブル設計、SQLAlchemy ORM活用
- **認証・認可**: JWT トークン、bcrypt パスワードハッシング、ロールベースアクセス制御
- **API設計**: RESTful API設計、エラーハンドリング
- **Docker環境構築**: docker-compose によるマルチコンテナ管理

## 学習プロセス

カリキュラム設計から実装、デバッグまでの全フェーズを **Claude Code（AIコーディングツール）** のサポートを受けて実施し、以下を学習しました。

- コード設計のベストプラクティスの習得
- エラー解決のアプローチ方法の理解
- 効率的な開発フローの構築
- セキュリティ考慮事項の意識向上

## 学習ポイント

このプロジェクトでの重要な学習内容

1. **認証の実装**: パスワードハッシング（bcrypt）と JWT トークンの組み合わせ
2. **ORM活用**: SQLAlchemy でのモデル定義とクエリ操作
3. **エラーハンドリング**: 適切なHTTPステータスコードと例外処理
4. **マイグレーション**: Alembic での DB スキーマ管理（オプション）
5. **コンテナ化**: Docker を使用した開発環境の統一

## 技術スタック

| 項目 | 技術 |
|------|------|
| フレームワーク | FastAPI |
| サーバー | Uvicorn |
| データベース | PostgreSQL |
| ORM | SQLAlchemy |
| 認証 | JWT (python-jose), bcrypt |
| コンテナ | Docker, docker-compose |

## プロジェクト構成

```
practice-fastapi/
├── main.py              # FastAPI メインアプリケーション
├── database.py          # データベース接続設定
├── models.py            # SQLAlchemy モデル定義
├── schemas.py           # Pydantic スキーマ定義
├── security.py          # 認証・認可処理
├── routers/
│   └── users.py         # ユーザー管理エンドポイント
├── requirements.txt     # Python依存パッケージ
├── Dockerfile           # Docker イメージ定義
├── compose.yml          # docker-compose 設定
└── curriculum/          # 学習カリキュラムメモ
```

## セットアップ

### 前提条件
- Docker & docker-compose がインストールされていること

### 起動方法

```bash
# リポジトリをクローン
git clone https://github.com/citronoct1st-wq/practice-fastapi.git
cd practice-fastapi

# コンテナを起動
docker-compose up -d

# APIサーバーが起動 (http://localhost:8000)
# Swagger UIで API ドキュメント確認可能 (http://localhost:8000/docs)
```

## API エンドポイント例

```bash
# ユーザー登録
POST /users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}

# ログイン
POST /users/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secure_password

# 認証済みユーザー情報取得
GET /users/me
Authorization: Bearer {access_token}
```

詳細はSwagger UI (`/docs`) をご覧ください。

## 参考資料

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Claude Code](https://claude.com/claude-code)

---
