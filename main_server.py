from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from jarvis_demo import get_response_with_tools


class CommandRequest(BaseModel):
    text: str = Field(min_length=1)


app = FastAPI(title="JARVIS Local API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
async def health_check():
    return {"status": "ready"}


@app.post("/command")
async def handle_command(request: CommandRequest):
    if not request.text.strip():
        raise HTTPException(status_code=422, detail="Command text must not be blank.")

    reply = await run_in_threadpool(get_response_with_tools, request.text)
    return {"reply": reply}
