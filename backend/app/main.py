from fastapi import FastAPI
from app.api import router
from app.cors_config import add_cors_middleware

app = FastAPI()
add_cors_middleware(app)
app.include_router(router)