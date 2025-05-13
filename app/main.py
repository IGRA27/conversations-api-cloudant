from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime
from .cloudant_client import db

# --- MODELOS ---
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

# --- APP ---
app = FastAPI(
    title="Chat Logger API",
    version="1.1.0",
    description="Guarda conversaciones en Cloudant; extiende en la misma sesión si el user_id ya existe."
)

@app.post(
    "/conversations",
    status_code=201,
    response_model=dict,
    summary="Guardar conversación completa",
    description="Recibe un user_id y un array de mensajes (`messages`) o el historial crudo (`session_history`).\
               Si ya existe un doc con ese user_id, **extiende** sus mensajes; si no, **crea** uno nuevo."
)
def store_conversation(conv: ConversationRequest):
    #1)Mapear el body a una lista de mensajes uniformes
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
        raise HTTPException(422, detail="`messages` o `session_history` es requerido")

    #2)Verificar si ya existe la conversación por user_id
    selector = {"selector": {"user_id": conv.user_id}}
    existing = list(db.get_query_result(selector))

    timestamp = datetime.utcnow().isoformat() + "Z"
    if existing:
        #Actualizamos el primer doc coincidente
        doc = existing[0]
        doc_id = doc["_id"]

        #Cargamos el documento completo
        record = db[doc_id]
        current = record.get("messages", [])
        current.extend(msgs)

        #Asignamos y guardamos
        record["messages"]   = current
        record["updated_at"] = timestamp
        success = record.save()  #retorna True/False
        if not success:
            raise HTTPException(500, detail="Error al actualizar en Cloudant")
        return {"id": doc_id, "ok": True}

    else:
        #Creamos un nuevo documento
        new_doc = {
            "user_id":    conv.user_id,
            "created_at": timestamp,
            "messages":   msgs
        }
        resp = db.create_document(new_doc)
        if not resp.exists():
            raise HTTPException(500, detail="Error al guardar en Cloudant")
        return {"id": resp["_id"], "ok": True}


@app.get(
    "/conversations",
    response_model=List[ConversationResponse],
    summary="Listar conversaciones",
    description="Trae todos los docs o, si se pasa `user_id`, sólo los de esa sesión."
)
def get_conversations(
    user_id: Optional[str] = Query(None, description="Filtrar por user_id")
):
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
