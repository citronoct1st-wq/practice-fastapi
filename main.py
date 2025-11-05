from fastapi import FastAPI
from database import SessionLocal
from sqlalchemy import text

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Docker + FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        # サーバ起動時にコンソールにメッセージを表示できる。
        print("✓ Database connected successfully!")
    finally:
        db.close()