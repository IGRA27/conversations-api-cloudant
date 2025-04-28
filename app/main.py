from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
from .cloudant_client import db

class Message(BaseModel):
    type: str   # "user" o "bot"
    text: str

class ConversationIn(BaseModel):
    user_email: EmailStr
    messages: List[Message]

app = FastAPI()

@app.post("/conversations/", status_code=201)
def store_conversation(conv: ConversationIn):
    doc = {
        "user_email": conv.user_email,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "messages": [m.dict() for m in conv.messages]
    }
    response = db.create_document(doc)
    if not response.exists():
        raise HTTPException(500, "Error al guardar en Cloudant")
    return {"id": response["_id"], "ok": True}

@app.get("/conversations/{email}", response_model=List[ConversationIn])
def get_conversations(email: EmailStr):
    #Consulta todos los docs con este user_email
    results = []
    for doc in db.get_query_result({"selector": {"user_email": email}}):
        results.append({
            "user_email": doc["user_email"],
            "messages": doc["messages"]
        })
    return results

@app.get("/conversations/", response_model=List[ConversationIn])
def get_all_conversations():
    #Trae todos los documentos (NOTA ISAAC:¡cuidado con volumen muy alto!)
    results = []
    for doc in db:
        results.append({
            "user_email": doc["user_email"],
            "messages": doc["messages"]
        })
    return results
