import os
import asyncio
from typing import Dict, Any, List
import httpx
from dotenv import load_dotenv
from uuid import uuid4
from utils.storage import read_json, write_json

# --- Archivos de datos ---
SESSIONS_FILE = "sessions.json"
PLAYERS_FILE = "players.json"

# --- Funciones de persistencia ---
def save_session(session_id: str, data: dict):
    sessions = read_json(SESSIONS_FILE)
    sessions[session_id] = data
    write_json(SESSIONS_FILE, sessions)

def load_session(session_id: str) -> dict | None:
    sessions = read_json(SESSIONS_FILE)
    return sessions.get(session_id)

def save_player(player_name: str, session_id: str):
    players = read_json(PLAYERS_FILE)
    players[player_name] = session_id
    write_json(PLAYERS_FILE, players)

def get_player_session(player_name: str) -> str | None:
    players = read_json(PLAYERS_FILE)
    return players.get(player_name)


# --- Configuración base ---
load_dotenv()
SRD_URL = os.getenv("SRD_SERVICE_URL", "https://sam-srdservice.onrender.com")

# Estado actual de la partida en memoria
GAME_STATE: Dict[str, Any] = {
    "running": False,
    "scene": "none",
    "party_levels": [],
    "log": []
}

# --- Comunicación con el SRDService ---
async def srd_get(path: str) -> Any:
    url = f"{SRD_URL}{path}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()

async def srd_post(path: str, payload: Dict[str, Any]) -> Any:
    url = f"{SRD_URL}{path}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return r.json()


# --- Funciones narrativas y de progreso ---
def update_story_state(new_data: dict):
    """Actualiza los elementos narrativos persistentes."""
    if "story_state" not in GAME_STATE:
        GAME_STATE["story_state"] = {}
    GAME_STATE["story_state"].update(new_data)
    save_session(GAME_STATE["session_id"], GAME_STATE)

def record_last_action(player: str, action: str):
    """Registra la última acción del jugador."""
    if "last_actions" not in GAME_STATE:
        GAME_STATE["last_actions"] = {}
    GAME_STATE["last_actions"][player] = action
    save_session(GAME_STATE["session_id"], GAME_STATE)


# --- Lógica principal del juego ---
async def start_game(party_levels: List[int]) -> Dict[str, Any]:
    if not party_levels:
        party_levels = [1]

    session_id = str(uuid4())

    GAME_STATE.update({
        "running": True,
        "scene": "intro",
        "party_levels": party_levels,
        "log": ["Partida iniciada"],
        "session_id": session_id,
        "story_state": {
            "location": "Aldea inicial",
            "objective": "Reunir al grupo",
            "events_completed": 0
        },
        "last_actions": {}
    })

    # Guardar sesión inicial
    save_session(session_id, GAME_STATE)

    # Comprobar que el SRDService está vivo
    health = await srd_get("/health")
    GAME_STATE["log"].append(f"SRD: {health.get('status', 'unknown')}")

    return {
        "message": "Nueva partida iniciada",
        "session_id": session_id,
        "party_levels": party_levels,
        "srd_status": health.get("status", "unknown")
    }


async def handle_action(player: str, action: str) -> Dict[str, Any]:
    # Buscar si el jugador ya tiene partida
    session_id = get_player_session(player)
    if not session_id and not GAME_STATE.get("running"):
        return {"error": "No hay partida en curso. Usa /game/start."}

    # Si no hay partida cargada en memoria, intenta restaurar
    if not GAME_STATE.get("running") and session_id:
        saved = load_session(session_id)
        if saved:
            GAME_STATE.update(saved)
            GAME_STATE["log"].append(f"{player} ha retomado la partida.")
        else:
            return {"error": "No se pudo cargar la sesión previa."}

    action_lower = action.strip().lower()
    GAME_STATE["log"].append(f"{player}: {action_lower}")
    save_player(player, GAME_STATE.get("session_id", "default"))
    record_last_action(player, action_lower)

    # Acción: combate
    if action_lower.startswith("combat"):
        _, *rest = action_lower.split()
        difficulty = rest[0] if rest else "medium"
        enc = await srd_post("/srd/encounter", {
            "party_levels": GAME_STATE["party_levels"],
            "difficulty": difficulty
        })

        GAME_STATE["last_encounter"] = enc
        update_story_state({
            "scene": "battlefield",
            "objective": f"Superar un combate {difficulty}",
            "events_completed": GAME_STATE["story_state"].get("events_completed", 0) + 1
        })

        save_session(GAME_STATE["session_id"], GAME_STATE)

        return {
            "scene": GAME_STATE["scene"],
            "n_monsters": len(enc.get("monsters", [])),
            "encounter": enc
        }

    # Acción: explorar
    if action_lower.startswith("explore") or action_lower.startswith("investigate"):
        update_story_state({
            "scene": "exploration",
            "objective": "Explorar el área cercana",
            "events_completed": GAME_STATE["story_state"].get("events_completed", 0) + 1
        })
        save_session(GAME_STATE["session_id"], GAME_STATE)
        return {
            "scene": "exploration",
            "narrative": f"{player} observa el entorno con atención. El aire es denso y las sombras se mueven entre los árboles.",
            "story_state": GAME_STATE.get("story_state", {})
        }

    # Acción: descansar
    if action_lower.startswith("rest"):
        update_story_state({
            "scene": "camp",
            "objective": "Descansar y recuperar fuerzas",
            "events_completed": GAME_STATE["story_state"].get("events_completed", 0) + 1
        })
        save_session(GAME_STATE["session_id"], GAME_STATE)
        return {
            "scene": "camp",
            "narrative": f"{player} descansa junto a la fogata. La noche transcurre tranquila, pero algo cruje en la oscuridad...",
            "story_state": GAME_STATE.get("story_state", {})
        }

    # Acción: consultar hechizo
    if action_lower.startswith("spell "):
        name = action[6:].strip()
        try:
            data = await srd_get(f"/srd/spells/{name}")
            return {"query": f"spell:{name}", "data": data}
        except httpx.HTTPStatusError:
            return {"query": f"spell:{name}", "error": "No encontrado en SRD"}

    # Acción: consultar monstruo
    if action_lower.startswith("monster "):
        name = action[8:].strip()
        try:
            data = await srd_get(f"/srd/monsters/{name}")
            return {"query": f"monster:{name}", "data": data}
        except httpx.HTTPStatusError:
            return {"query": f"monster:{name}", "error": "No encontrado en SRD"}

    # Acción genérica
    return {
        "scene": GAME_STATE["scene"],
        "echo": action,
        "story_state": GAME_STATE.get("story_state", {})
    }


def get_state() -> Dict[str, Any]:
    """Devuelve el estado actual de la partida."""
    return {
        "running": GAME_STATE["running"],
        "scene": GAME_STATE["scene"],
        "party_levels": GAME_STATE["party_levels"],
        "story_state": GAME_STATE.get("story_state", {}),
        "last_actions": GAME_STATE.get("last_actions", {}),
        "log": GAME_STATE["log"][-10:],
        "session_id": GAME_STATE.get("session_id", None)
    }
