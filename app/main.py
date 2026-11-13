"""API du lab : relaie la conversation vers Ollama et sert l'interface web."""
import json, logging, os, time
import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
MODEL = os.environ.get("MODEL", "llama3.2:3b")
ACCESS_CODE = os.environ.get("ACCESS_CODE", "")
VERSION = os.environ.get("APP_VERSION", "dev")
SYSTEM = os.environ.get("SYSTEM_PROMPT",
                        "Tu es un assistant utile. Réponds en français, de façon concise.")
MAX_MESSAGES, MAX_CARACTERES = 20, 4000

logging.basicConfig(level=logging.INFO, format="%(message)s")
app = FastAPI(title="LLM Lab")
ICI = os.path.dirname(__file__)


class Conversation(BaseModel):
    messages: list[dict]


async def flux_ollama(messages):
    """Produit le texte généré, morceau par morceau."""
    corps = {"model": MODEL, "messages": messages, "stream": True}
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=corps) as r:
            r.raise_for_status()
            async for ligne in r.aiter_lines():
                if ligne:
                    yield json.loads(ligne).get("message", {}).get("content", "")


async def modele_pret():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            return any(m["name"] == MODEL for m in r.json().get("models", []))
    except Exception:
        return False


def valider(messages):
    if not messages or len(messages) > MAX_MESSAGES:
        raise HTTPException(422, f"entre 1 et {MAX_MESSAGES} messages")
    for m in messages:
        if m.get("role") not in ("user", "assistant") or not isinstance(m.get("content"), str):
            raise HTTPException(422, "message invalide")
        if len(m["content"]) > MAX_CARACTERES:
            raise HTTPException(422, f"message de plus de {MAX_CARACTERES} caractères")
    return [{"role": m["role"], "content": m["content"]} for m in messages]


@app.get("/")
def accueil():
    return FileResponse(os.path.join(ICI, "static", "index.html"))


@app.get("/api/health")
async def health():
    return {"ok": True, "version": VERSION, "modele": MODEL, "modele_pret": await modele_pret()}


@app.post("/api/chat")
async def chat(conv: Conversation, x_access_code: str = Header(default="")):
    if ACCESS_CODE and x_access_code != ACCESS_CODE:
        raise HTTPException(401, "code d'accès invalide")
    messages = [{"role": "system", "content": SYSTEM}] + valider(conv.messages)

    async def generer():
        debut, n = time.time(), 0
        try:
            async for morceau in flux_ollama(messages):
                n += len(morceau)
                yield morceau
        except httpx.HTTPError as e:
            yield f"\n[erreur du serveur de modèle : {type(e).__name__}]"
        logging.info(json.dumps({"evenement": "chat", "version": VERSION, "modele": MODEL,
                                 "caracteres": n, "duree_s": round(time.time() - debut, 1)}))

    return StreamingResponse(generer(), media_type="text/plain; charset=utf-8")
