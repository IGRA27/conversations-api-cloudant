from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .cloudant_client import db

#Modelo para cada turno bruto que envía Orchestrate
class Turn(BaseModel):
    u: Optional[str] = None   #mensaje del usuario
    a: Optional[str] = None   #mensaje del asistente

#Modelo interno de mensaje mapeado
class Message(BaseModel):
    type: str   #"user" o "assistant"
    text: str

#Request model: recibimos el historial crudo
class Conversation(BaseModel):
    user_id: str
    session_history: List[Turn]

app = FastAPI()

def map_sessions_to_messages(session_history: List[Turn]) -> List[dict]:
    """
    Convierte la lista de Turn {u,a} en la lista de Message {type,text}.
    """
    msgs = []
    for t in session_history:
        if t.u is not None:
            msgs.append({"type": "user",      "text": t.u})
        if t.a is not None:
            msgs.append({"type": "assistant", "text": t.a})
    return msgs

@app.post("/conversations/", status_code=201)
def store_conversation(conv: Conversation):
    #1)Mapea session_history → msgs
    msgs = map_sessions_to_messages(conv.session_history)

    #2)Usa conv.user_id como _id para upsert
    doc_id = conv.user_id

    if db.document_exists(doc_id):
        #Actualiza documento existente
        doc = db[doc_id]
        doc["messages"]  = msgs
        doc["timestamp"] = datetime.utcnow().isoformat() + "Z"
        doc.save()
    else:
        #Crea uno nuevo
        new_doc = {
            "_id": doc_id,
            "user_id": conv.user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "messages": msgs
        }
        resp = db.create_document(new_doc)
        if not resp.exists():
            raise HTTPException(500, "Error al guardar en Cloudant")

    return {"id": doc_id, "ok": True}

@app.get("/conversations/", response_model=List[dict])
def get_conversations(user_id: Optional[str] = Query(None, description="Filtrar por user_id")):
    #Recupera todos o filtra por user_id
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
