from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .cloudant_client import db

class Message(BaseModel):
    type: str   # p.e. "user" o "assistant"
    text: str

class Conversation(BaseModel):
    user_id: str
    messages: List[Message]

app = FastAPI()

@app.post("/conversations/", status_code=201, response_model=dict)
def store_conversation(conv: Conversation):
    doc = {
        "user_id":  conv.user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "messages": [m.dict() for m in conv.messages]
    }
    resp = db.create_document(doc)
    if not resp.exists():
        raise HTTPException(status_code=500, detail="Error al guardar en Cloudant")
    return {"id": resp["_id"], "ok": True}

@app.get("/conversations/", response_model=List[Conversation])
def get_conversations(user_id: Optional[str] = Query(None, description="Filtrar por user_id")):
    results = []
    if user_id:
        selector = {"selector": {"user_id": user_id}}
        docs = db.get_query_result(selector)
    else:
        docs = db
    for d in docs:
        results.append({
            "user_id":  d.get("user_id"),
            "messages": d.get("messages", [])
        })
    return results
