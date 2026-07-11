from fastapi import FastAPI

app = FastAPI(
    title="AI Insider Threat Behavioral Intelligence System",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "AI Insider Threat Behavioral Intelligence System API Running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }