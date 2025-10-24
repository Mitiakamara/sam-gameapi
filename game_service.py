# sam-gameapi/game_service.py
from utils import storage
from ai_engine import interpret_action

# ================================================================
# 🎮 Función: start_game
# ================================================================
async def start_game(party_levels: list[int]):
    """Inicia una nueva partida, guardando un estado base."""
    game_state = {
        "party_levels": party_levels,
        "scene": "Inicio de la aventura",
        "description": "Un viento gélido sopla sobre el valle de Pelvuria...",
        "history": [],
    }
    storage.write_json("game_state.json", game_state)
    return {"message": "Partida iniciada.", "state": game_state}

# ================================================================
# ⚔️ Función: handle_action
# ================================================================
async def handle_action(player: str, action: str, mode: str = "action"):
    """
    Procesa una acción o diálogo de un jugador.
    Envia el texto a GPT-5 para interpretación narrativa.
    """
    # Leer estado del juego (opcional)
    game_state = storage.read_json("game_state.json")
    context = {
        "scene": game_state.get("scene", "Ubicación desconocida"),
        "description": game_state.get("description", "Sin detalles."),
    }

    # Interpretar usando la IA
    narration = await interpret_action(player, action, mode, context)

    # Guardar en historial
    history = game_state.get("history", [])
    history.append({"player": player, "action": action, "response": narration})
    game_state["history"] = history
    storage.write_json("game_state.json", game_state)

    return {"player": player, "action": action, "result": narration}
