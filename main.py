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