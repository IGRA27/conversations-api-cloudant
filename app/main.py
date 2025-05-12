from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime
from .cloudant_client import db

#crudo desde Orchestrate
class Turn(BaseModel):
    u: Optional[str] = None
    a: Optional[str] = None

#nuestro existente Message model
class Message(BaseModel):
    type: str   # "user" | "assistant"
    text: str

#Updated Conversation: either messages _or_ session_history is allowed
class Conversation(BaseModel):
    user_id: str
    messages: Optional[List[Message]]      = None
    session_history: Optional[List[Turn]]  = None

app = FastAPI()

@app.post("/conversations/", status_code=201, response_model=dict)
def store_conversation(conv: Conversation):
    #1)si pasa crudo session_history, mapeamos
    if conv.session_history:
        msgs: List[dict] = []
        for t in conv.session_history:
            if t.u is not None:
                msgs.append({"type":"user",      "text":t.u})
            if t.a is not None:
                msgs.append({"type":"assistant", "text":t.a})
    #2)Caso contrario enviamos mapeado el message
    elif conv.messages:
        msgs = [m.dict() for m in conv.messages]
    else:
        raise HTTPException(422, detail="Either messages or session_history is required")

    #3)Guardar to Cloudant
    doc = {
        "user_id":  conv.user_id,
        "timestamp": datetime.utcnow().isoformat()+"Z",
        "messages": msgs
    }
    resp = db.create_document(doc)
    if not resp.exists():
        raise HTTPException(500, "Error al guardar en Cloudant")
    return {"id": resp["_id"], "ok": True}

@app.get("/conversations/", response_model=List[Union[Conversation, dict]])
def get_conversations(user_id: Optional[str] = Query(None)):
    if user_id:
        selector = {"selector": {"user_id": user_id}}
        docs = db.get_query_result(selector)
    else:
        docs = db
    results = []
    for d in docs:
        results.append({
            "user_id":  d.get("user_id"),
            "messages": d.get("messages", [])
        })
    return results