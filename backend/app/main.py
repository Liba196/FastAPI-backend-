from fastapi import FastAPI , Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from fastapi.security import HTTPBearer
from app.api.users import router as users_router
from app.api.documents import router as documents_router






# JavaScript from calling a different-origin API unless the API
# explicitly allows it via these headers — that's what CORS is.
# Once the widget has a real dev URL (Step 9 follow-up), restrict
# allow_origins to that exact URL instead of "*", and definitely
# before this goes anywhere near production (Phase 11 of the blueprint).


app = FastAPI()

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(users_router)
app.include_router(documents_router)

@app.get("/")
def read_root():
    return {"message": "POESSA Legal RAG API is alive"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://poessaproject.netlify.app",
    "http://127.0.0.1:5500/Admin/index.html",
    "https://poessaproject.netlify.app"  # <-- Paste your exact Netlify link here
]

# 2. Add the middleware config directly after creating the app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Or use ["*"] to temporarily open it wide for debugging
    allow_credentials=True,
    allow_methods=["*"],           # Crucial: Allows the OPTIONS preflight method
    allow_headers=["*"],           # Crucial: Allows Content-Type and custom auth headers
)

app.include_router(chat_router)


