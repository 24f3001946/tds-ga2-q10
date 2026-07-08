from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------

allowed_origins = [
    "https://app-99u34m.example.com",

    # Keep this so IITM exam page can access your API.
    # Replace with the actual origin if the instructions specify one.
    "https://exam.sanand.workers.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Rate Limiter
# -----------------------------

RATE_LIMIT = 10
WINDOW = 10

clients = {}

# -----------------------------
# Request Context + Rate Limit
# -----------------------------

@app.middleware("http")
async def request_context(request: Request, call_next):

    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    client = request.headers.get("X-Client-Id", "anonymous")
    now = time.time()

    if client not in clients:
        clients[client] = []

    clients[client] = [t for t in clients[client] if now - t < WINDOW]

    if len(clients[client]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"X-Request-ID": request_id},
        )

    clients[client].append(now)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
# -----------------------------
# Endpoint
# -----------------------------

@app.get("/ping")
async def ping(request: Request):
    return {
        "email": "24f3001946@ds.study.iitm.ac.in",
        "request_id": request.state.request_id
    }
