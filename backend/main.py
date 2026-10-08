from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hackathon API",
    version="0.1.0",
    description="API для приложения трекинга привычек",
)

# CORS — на хакатоне открываем всё, чтобы фронт с любого порта ходил
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["🩺 System"], description="Healthcheck")
async def health() -> dict[str, str]:
    """Проверка, что сервер запустился."""
    return {"status": "ok"}


# TODO: раскомментировать, когда лид починит hash-argon.py → hash_argon.py
# from src.users.router import router as users_router
# app.include_router(users_router, prefix="/api")