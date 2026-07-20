from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router


# DEV ONLY: allows requests from any origin. Browsers block frontend
# JavaScript from calling a different-origin API unless the API
# explicitly allows it via these headers — that's what CORS is.
# Once the widget has a real dev URL (Step 9 follow-up), restrict
# allow_origins to that exact URL instead of "*", and definitely
# before this goes anywhere near production (Phase 11 of the blueprint).

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "POESSA Legal RAG API is alive"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
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


