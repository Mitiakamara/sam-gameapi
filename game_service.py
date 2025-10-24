# sam-gameapi/game_service.py
from utils import storage
from ai_engine import interpret_action
from core.event_system import EventSystem

# ================================================================
# 🎮 INICIO DEL JUEGO
# ================================================================
async def start_game(party_levels: list[int]):
    """Inicia una nueva partida, reseteando el estado base."""
    game_state = {
        "party_levels": party_levels,
        "scene": "Inicio de la aventura",
        "description": "Una brisa fría recorre el valle mientras el grupo se prepara para lo desconocido.",
        "history": []
    }
    storage.write_json("game_state.json", game_state)
    return {"message": "Partida iniciada.", "state": game_state}

# ================================================================
# ⚔️ ACCIONES DE JUGADOR
# ================================================================
async def handle_action(player: str, action: str, mode: str = "action"):
    """
    Procesa una acción o diálogo de un jugador y devuelve la respuesta narrativa.
    También puede detonar eventos dinámicos aleatorios.
    """
    # Leer estado actual del juego
    game_state = storage.read_json("game_state.json")
    context = {
        "scene": game_state.get("scene", "Ubicación desconocida"),
        "description": game_state.get("description", "Sin detalles.")
    }

    # Interpretar la acción mediante S.A.M. (IA narrativa)
    narration = await interpret_action(player, action, mode, context)

    # Guardar en historial
    history = game_state.get("history", [])
    history.append({"player": player, "action": action, "response": narration})
    game_state["history"] = history
    storage.write_json("game_state.json", game_state)

    # Determinar si se debe generar un evento aleatorio
    event_triggered = _should_trigger_event(action, len(history))

    event_result = None
    if event_triggered:
        event_result = await _generate_dynamic_event(context)

    response_data = {"player": player, "result": narration}

    if event_result:
        response_data["event"] = event_result

    return response_data

# ================================================================
# 🎲 EVENTOS DINÁMICOS
# ================================================================
async def _generate_dynamic_event(context: dict) -> dict:
    """
    Genera un evento aleatorio y lo pasa por la IA para narrarlo.
    """
    event_system = EventSystem()
    event = event_system.generate_event(context)

    # Pasar el evento al narrador para interpretación
    event_narration = await interpret_action("S.A.M.", event["description"], "action", context)

    # Guardar el evento en el estado global
    game_state = storage.read_json("game_state.json")
    history = game_state.get("history", [])
    history.append({
        "player": "S.A.M.",
        "action": f"[Evento] {event['title']}",
        "response": event_narration
    })
    game_state["history"] = history
    storage.write_json("game_state.json", game_state)

    return {
        "event_title": event["title"],
        "event_type": event["type"],
        "event_description": event["description"],
        "event_narration": event_narration
    }

# ================================================================
# 🧩 LÓGICA DE ACTIVACIÓN DE EVENTOS
# ================================================================
def _should_trigger_event(action_text: str, action_count: int) -> bool:
    """
    Define si debe generarse un evento dinámico tras una acción.
    Criterios:
      - Pequeña probabilidad aleatoria (10%)
      - O cada 5 acciones del grupo
    """
    import random

    if action_count % 5 == 0:
        return True
    elif random.random() < 0.1:
        return True
    elif any(word in action_text.lower() for word in ["exploro", "investigo", "camino", "avanzar", "viajar"]):
        return random.random() < 0.3
    return False
