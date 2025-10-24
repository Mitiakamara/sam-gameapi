# sam-gameapi/core/event_system.py
import random
from datetime import datetime
from utils import storage
from core.encounter_tables import EXPLORATION_EVENTS, COMBAT_EVENTS, SOCIAL_EVENTS, WEATHER_EVENTS


class EventSystem:
    """
    Sistema de generación de eventos dinámicos.
    Selecciona y crea eventos según tipo, contexto o probabilidad.
    """

    def __init__(self):
        self.event_log_file = "event_log.json"

    # ============================================================
    # 🎲 FUNCIÓN PRINCIPAL
    # ============================================================
    def generate_event(self, context: dict | None = None) -> dict:
        """
        Genera un evento aleatorio según el contexto actual.
        Devuelve un dict con el evento elegido.
        """
        event_type = self._select_event_type()
        event_table = self._get_table(event_type)
        event = random.choice(event_table)

        event_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "title": event["title"],
            "description": event["description"],
        }

        # Registrar evento en log local
        self._log_event(event_entry)

        return event_entry

    # ============================================================
    # 🔮 SELECCIÓN DE TIPO DE EVENTO
    # ============================================================
    def _select_event_type(self) -> str:
        """
        Define el tipo de evento a generar según probabilidad.
        """
        roll = random.random()
        if roll < 0.5:
            return "exploration"
        elif roll < 0.75:
            return "social"
        elif roll < 0.9:
            return "weather"
        else:
            return "combat"

    # ============================================================
    # 📜 TABLAS DE EVENTOS
    # ============================================================
    def _get_table(self, event_type: str) -> list[dict]:
        """
        Devuelve la tabla correspondiente al tipo de evento.
        """
        if event_type == "exploration":
            return EXPLORATION_EVENTS
        elif event_type == "combat":
            return COMBAT_EVENTS
        elif event_type == "social":
            return SOCIAL_EVENTS
        elif event_type == "weather":
            return WEATHER_EVENTS
        else:
            return []

    # ============================================================
    # 🧾 REGISTRO EN LOG LOCAL
    # ============================================================
    def _log_event(self, event: dict):
        """
        Guarda el evento generado en un archivo JSON local.
        """
        data = storage.read_json(self.event_log_file)
        events = data.get("events", [])
        events.append(event)
        data["events"] = events
        storage.write_json(self.event_log_file, data)
