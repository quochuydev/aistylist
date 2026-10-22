from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from . import agent

app = FastAPI()


@app.get("/stylist")
async def stylist_endpoint(prompt: str = Query(min_length=3, max_length=1000)):
    return StreamingResponse(agent.stylist(prompt), media_type="text/event-stream")


class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    looks: list = Field(max_length=5)


@app.post("/ask")
async def ask_endpoint(body: Ask):
    return await agent.ask(body.question, body.looks)
