from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import create_tables
from app.routers import auth, tasks, admin

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.on_event("startup")
# def on_startup():
#     create_tables()



app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(admin.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
