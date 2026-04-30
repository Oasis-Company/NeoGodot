import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes.sessions import router as sessions_router
from routes.plan import router as plan_router
from routes.tasks import router as tasks_router
from routes.events import router as events_router
from routes.imports import router as imports_router
from routes.questions import router as questions_router

load_dotenv()

app = FastAPI(
    title="Neo Runtime Gateway",
    description="Unified AI runtime gateway for NeoGodot and Trae",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router, prefix="/v1")
app.include_router(plan_router, prefix="/v1")
app.include_router(tasks_router, prefix="/v1")
app.include_router(events_router, prefix="/v1")
app.include_router(imports_router, prefix="/v1")
app.include_router(questions_router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "neo_runtime_gateway"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 7777))
    uvicorn.run(app, host=host, port=port)