from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

# 環境変数からDB接続情報を取得
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "db")  # Docker内のサービス名
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "fastapi_db")

# PostgreSQL接続文字列
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy エンジン作成
engine = create_engine(DATABASE_URL, poolclass=NullPool)

# セッション作成用の関数
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM モデルの基底クラス
Base = declarative_base()

# FastAPIで使用する依存性注入用関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()