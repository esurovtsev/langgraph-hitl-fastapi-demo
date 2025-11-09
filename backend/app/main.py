from fastapi import FastAPI
from app.lesson_01_blocking import router as lesson_01_router
from app.lesson_02_streaming import router as lesson_02_router
from app.lesson_03_async_mcp import router as lesson_03_router
from app.cors_config import add_cors_middleware

app = FastAPI()
add_cors_middleware(app)

# Register lesson routers
app.include_router(lesson_01_router)
app.include_router(lesson_02_router)
app.include_router(lesson_03_router)