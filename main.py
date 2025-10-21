from fastapi import FastAPI
from pydantic import BaseModel
from game_service import start_game, handle_action

app = FastAPI(title="S.A.M. Game API", version="1.0")

# ✅ Endpoint de salud
@app.get("/health")
def health_check():
    return {"message": "API online", "status": "ready"}

# ---- Modelos ----
class StartRequest(BaseModel):
    party_levels: list[int] | None = None

class ActionRequest(BaseModel):
    player: str
    action: str

# ---- Endpoints ----
@app.post("/game/start")
async def api_start(payload: StartRequest):
    """Inicia una nueva partida"""
    return await start_game(payload.party_levels or [1])

@app.post("/game/action")
async def api_action(payload: ActionRequest):
    """Procesa acciones de los jugadores"""
    return await handle_action(payload.player, payload.action)
