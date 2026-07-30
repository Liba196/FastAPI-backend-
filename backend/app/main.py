from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from fastapi.security import HTTPBearer
from app.api.users import router as users_router
from app.api.documents import router as documents_router

app = FastAPI()

# 1. ALWAYS REGISTER MIDDLEWARE FIRST
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://poessaproject.netlify.app",
    "https://poessa-admin-dashboard.netlify.app",
    "https://poessaproject.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         
    allow_credentials=True,
    allow_methods=["*"],           
    allow_headers=["*"],           
)

# 2. INCLUDE ROUTERS AFTER MIDDLEWARE
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(users_router)
app.include_router(documents_router)
app.include_router(chat_router)

@app.get("/")
def read_root():
    return {"message": "POESSA Legal RAG API is alive"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
