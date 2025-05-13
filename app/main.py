from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime, timedelta
from .cloudant_client import db

# --- Parámetro de configuración: cuántas horas dura una "misma" conversación
CONVERSATION_TIMEOUT_HOURS = 3

# --- Modelos ---
class Turn(BaseModel):
    u: Optional[str] = None
    a: Optional[str] = None

class Message(BaseModel):
    type: str   # "user" | "assistant"
    text: str

class ConversationRequest(BaseModel):
    user_id: str
    messages: Optional[List[Message]]     = None
    session_history: Optional[List[Turn]] = None

class ConversationResponse(BaseModel):
    user_id: str
    messages: List[Message]

# --- App & rutas ---
app = FastAPI()

@app.post(
    "/conversations",
    status_code=201,
    response_model=dict,
    summary="Guardar o extender conversación"
)
def store_conversation(conv: ConversationRequest):
    #1)Mapeo uniforme de mensajes
    msgs: List[dict] = []
    if conv.session_history:
        for t in conv.session_history:
            if t.u:
                msgs.append({"type": "user",      "text": t.u})
            if t.a:
                msgs.append({"type": "assistant", "text": t.a})
    elif conv.messages:
        msgs = [m.dict() for m in conv.messages]
    else:
        raise HTTPException(422, detail="Se requiere `messages` o `session_history`")

    #2)Determinar “ahora” y el umbral de corte
    now    = datetime.utcnow()
    cutoff = now - timedelta(hours=CONVERSATION_TIMEOUT_HOURS)

    #3)Buscar todos los docs del mismo user_id
    selector = {"selector": {"user_id": conv.user_id}}
    docs = list(db.get_query_result(selector))

    #4)Filtrar los documentos “recientes” (updated_at o created_at ≥ cutoff)
    candidates = []
    for d in docs:
        ts_str = d.get("updated_at") or d.get("created_at")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", ""))
        except:
            continue
        if ts >= cutoff:
            candidates.append((ts, d))

    if candidates:
        #5a)Extender el doc más reciente
        candidates.sort(key=lambda x: x[0], reverse=True)
        doc = candidates[0][1]
        record = db[doc["_id"]]           # arga el documento completo
        current = record.get("messages", [])
        current.extend(msgs)              #Añade sólo los nuevos mensajes
        record["messages"]   = current
        record["updated_at"] = now.isoformat() + "Z"
        success = record.save()
        if not success:
            raise HTTPException(500, detail="Error al actualizar en Cloudant")
        return {"id": doc["_id"], "ok": True}

    else:
        #5b)Crear un nuevo documento
        payload = {
            "user_id":    conv.user_id,
            "created_at": now.isoformat() + "Z",
            "updated_at": now.isoformat() + "Z",
            "messages":   msgs
        }
        resp = db.create_document(payload)
        if not resp.exists():
            raise HTTPException(500, detail="Error al crear en Cloudant")
        return {"id": resp["_id"], "ok": True}


@app.get(
    "/conversations",
    response_model=List[ConversationResponse],
    summary="Listar conversaciones"
)
def get_conversations(user_id: Optional[str] = Query(None, description="Filtrar por user_id")):
    if user_id:
        selector = {"selector": {"user_id": user_id}}
        docs = db.get_query_result(selector)
    else:
        docs = db

    out: List[ConversationResponse] = []
    for d in docs:
        msgs = [ Message(type=m["type"], text=m["text"]) for m in d.get("messages", []) ]
        out.append(ConversationResponse(user_id=d["user_id"], messages=msgs))
    return out
