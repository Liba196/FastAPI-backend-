from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "POESSA Legal RAG API is alive"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}