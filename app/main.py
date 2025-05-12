from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.scheduler import start_scheduler
from api.routes import router as api_router

# pip freeze > requirements.txt
# pip install -r requirements.txt
# uvicorn app.main:app --reload
# uvicorn app.main:app --host 0.0.0.0 --port 443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem

@asynccontextmanager
async def lifespan(app: FastAPI):
    # при старті
    start_scheduler()

    yield

    # при завершенні
    # stop_scheduler()
    # await cleanup()
app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

@app.get("/")
def root():
    return {"status": "Festigo backend is running"}