# sam-gameapi/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from game_service import start_game, handle_action
from utils import storage

app = FastAPI(title="S.A.M. Game API", version="1.2")

# ======================================================
# 🩺 Endpoint de salud
# ======================================================
@app.get("/health")
def health_check():
    return {"message": "API online", "status": "ready"}

# ======================================================
# 🎮 Modelos
# ======================================================
class StartRequest(BaseModel):
    party_levels: List[int] | None = None

class ActionRequest(BaseModel):
    player: str
    action: str

class PlayerAction(BaseModel):
    player: str

# ======================================================
# 🎲 ENDPOINTS DE JUEGO
# ======================================================
@app.post("/game/start")
async def api_start(payload: StartRequest):
    """Inicia una nueva partida"""
    return await start_game(payload.party_levels or [1])

@app.post("/game/action")
async def api_action(payload: ActionRequest):
    """Procesa acciones de los jugadores"""
    return await handle_action(payload.player, payload.action)

# ======================================================
# 🧙‍♂️ ENDPOINTS DE PARTY
# ======================================================
PARTY_FILE = "party.json"

@app.get("/party")
def get_party():
    """Obtiene el estado actual del grupo"""
    data = storage.read_json(PARTY_FILE)
    return {"party": data.get("players", [])}

@app.post("/party/join")
def join_party(payload: PlayerAction):
    """Agrega un jugador al grupo"""
    data = storage.read_json(PARTY_FILE)
    players = data.get("players", [])

    if payload.player in players:
        raise HTTPException(status_code=400, detail="Jugador ya está en el grupo.")

    players.append(payload.player)
    storage.write_json(PARTY_FILE, {"players": players})
    return {"message": f"{payload.player} se unió al grupo.", "party": players}

@app.post("/party/leave")
def leave_party(payload: PlayerAction):
    """Un jugador deja el grupo"""
    data = storage.read_json(PARTY_FILE)
    players = data.get("players", [])

    if payload.player not in players:
        raise HTTPException(status_code=404, detail="Jugador no está en el grupo.")

    players.remove(payload.player)
    storage.write_json(PARTY_FILE, {"players": players})
    return {"message": f"{payload.player} dejó el grupo.", "party": players}

@app.post("/party/kick")
def kick_player(payload: PlayerAction):
    """Expulsa a un jugador del grupo"""
    data = storage.read_json(PARTY_FILE)
    players = data.get("players", [])

    if payload.player not in players:
        raise HTTPException(status_code=404, detail="Jugador no está en el grupo.")

    players.remove(payload.player)
    storage.write_json(PARTY_FILE, {"players": players})
    return {"message": f"{payload.player} fue expulsado del grupo.", "party": players}

@app.post("/party/reset")
def reset_party():
    """Limpia completamente el grupo"""
    storage.write_json(PARTY_FILE, {"players": []})
    return {"message": "Grupo limpiado.", "party": []}

# ======================================================
# 🔚 FIN
# ======================================================
