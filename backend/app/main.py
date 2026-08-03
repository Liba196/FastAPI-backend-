from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from fastapi.security import HTTPBearer
from app.api.users import router as users_router
from app.api.documents import router as documents_router

app = FastAPI()

# 1. STRICT allowlist — used for everything EXCEPT the public chat/health
#    endpoints below. Admin panel, auth, user management, document
#    management all stay locked to these known, trusted origins.
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://poessaproject.netlify.app",
    "https://poessa-admin-dashboard.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. OPEN CORS for the public, embeddable chat widget — deliberately NOT
#    restricted to the allowlist above. This is what makes "embed the
#    widget on any website" actually true: /api/v1/chat requires no
#    login/cookies/tokens, so there's no sensitive credential at risk
#    from allowing any origin to call it. Admin/auth endpoints are NEVER
#    covered by this — they always go through the strict CORSMiddleware
#    above instead.
#
#    Registered AFTER CORSMiddleware, which makes it the OUTERMOST layer —
#    it runs first, and for these two paths it answers directly (including
#    the OPTIONS preflight) without ever reaching the strict CORSMiddleware.
#    Every other path falls through to CORSMiddleware exactly as before.
OPEN_CORS_PATHS = {"/api/v1/chat", "/api/v1/health"}


@app.middleware("http")
async def open_cors_for_public_widget(request: Request, call_next):
    if request.url.path in OPEN_CORS_PATHS:
        if request.method == "OPTIONS":
            return Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Max-Age": "600",
                },
            )
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    return await call_next(request)


# 3. INCLUDE ROUTERS AFTER MIDDLEWARE
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