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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


