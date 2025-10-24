# 🧙‍♀️ S.A.M. GameAPI

Este servicio es el **motor de juego principal** del proyecto **S.A.M. (Storytelling Adventure Master)**.  
Está diseñado para actuar como intermediario entre el bot de Telegram y el SRDService de D&D 5.2.1,  
gestionando las partidas, los jugadores, los encuentros y el progreso narrativo.

---

## 🚀 Características

- API basada en **FastAPI** (Python 3.11)
- Integración directa con **SRDService** para hechizos, monstruos y encuentros
- Soporte para partidas persistentes con múltiples jugadores
- Estado narrativo guardado (escena, objetivo, progreso)
- Preparada para integrar campañas SRD 5.1 / 5.2.1

---

## ⚙️ Endpoints principales

| Método | Ruta | Descripción |
|--------|------|--------------|
| `GET` | `/health` | Verifica el estado del servicio |
| `POST` | `/game/start` | Inicia una nueva partida |
| `POST` | `/game/action` | Envía una acción del jugador |
| `GET` | `/game/state` | Devuelve el estado actual |
| `POST` | `/game/load_campaign` *(futuro)* | Carga una campaña predefinida |

---

