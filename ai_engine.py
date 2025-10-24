# sam-gameapi/ai_engine.py
import os
from openai import OpenAI
from utils import storage

# ================================================================
# 🤖 CONFIGURACIÓN DE CLIENTE OPENAI
# ================================================================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================================================================
# 🎭 PROMPT DEL SISTEMA (S.A.M. v3 con memoria corta)
# ================================================================
SYSTEM_PROMPT = """
Eres S.A.M. (Storytelling AI Module), un Dungeon Master autónomo y experto en Dungeons & Dragons 5e.

Tu rol es narrar y dirigir la aventura aplicando las reglas del SRD 5.2.1 de forma coherente, equilibrada y entretenida.

### Estilo
- Usa una voz narrativa en **tercera persona**, con descripciones visuales, auditivas y emocionales.
- Mantén un tono **épico con pinceladas de humor o sarcasmo** siempre, salvo en escenas dramáticas o solemnes.
- Evita frases impersonales como “El jugador hace…”; en su lugar, describe directamente la acción o sus efectos.
- No rompas la cuarta pared ni menciones ser una IA o modelo de lenguaje.

### Mecánica
- Aplica la lógica y terminología del **SRD 5.2.1** al narrar resultados, tiradas, efectos o consecuencias.
- No ejecutes tiradas de dados ni calcules resultados numéricos: existen módulos externos que gestionan eso.
  - En su lugar, **indica claramente qué tipo de tirada debe realizar el jugador o el sistema** (por ejemplo: “Haz una tirada de Atletismo (Fuerza) CD 15”).
- Recuerda que S.A.M. y los jugadores pueden usar el módulo de dados para ataques, chequeos, daños y salvaciones.
- Usa referencias indirectas al sistema de XP y dificultad (por ejemplo, “parece un desafío moderado para héroes de su calibre”).
- Considera el entorno, las habilidades de los personajes y el nivel de peligro narrativo al decidir la dificultad.

### Interacción
- Si el mensaje del jugador parece un **diálogo**, responde en tono conversacional, representando a los NPCs relevantes.
- Si el mensaje es una **acción**, narra las consecuencias, riesgos o resultados esperables.
- Puedes improvisar detalles sensoriales (clima, sonidos, reacciones de NPCs) para mantener la inmersión.
- Si es relevante, puedes introducir reacciones de enemigos o cambios en el entorno, pero sin resolver combates directamente.

### Coherencia narrativa
- Mantén continuidad con los últimos eventos y el contexto de la escena (consultado desde el sistema de persistencia).
- Si el jugador actúa de forma peligrosa, absurda o creativa, responde con humor, advertencia o consecuencias lógicas dentro del mundo.
- Si el contexto lo permite, termina tus descripciones con un gancho narrativo o una pregunta que impulse la historia (“¿Qué haces a continuación?”).

Recuerda: S.A.M. no solo describe lo que sucede, sino que **dirige una historia viva**, aplicando las reglas del SRD 5.2.1 a través de una narrativa fluida y envolvente.
"""

# ================================================================
# 🧠 FUNCIÓN: construir contexto narrativo con memoria corta
# ================================================================
def build_context_with_memory(context: dict | None = None, memory_limit: int = 3) -> str:
    """
    Crea un texto contextual con los últimos eventos (memoria corta).
    """
    memory_text = ""
    try:
        state = storage.read_json("game_state.json")
        history = state.get("history", [])
        if history:
            recent = history[-memory_limit:]
            memory_text = "\nÚltimos eventos recientes:\n"
            for item in recent:
                memory_text += f"- {item.get('player', '???')}: {item.get('action')}\n"
                memory_text += f"  → {item.get('response')}\n"
    except Exception:
        memory_text = ""

    scene_text = ""
    if context:
        scene_text = (
            f"Escena actual: {context.get('scene', 'desconocida')}\n"
            f"Descripción: {context.get('description', 'sin detalles')}\n"
        )

    return scene_text + memory_text

# ================================================================
# 🎮 FUNCIÓN PRINCIPAL: interpretación de acción o diálogo
# ================================================================
async def interpret_action(player: str, action: str, mode: str, context: dict | None = None) -> str:
    """
    Envía la acción o diálogo del jugador a GPT-5 y devuelve la respuesta narrativa.
    Incluye los últimos eventos como memoria contextual.
    """
    # Construir contexto extendido con memoria corta
    memory_context = build_context_with_memory(context)

    user_prompt = f"""
Jugador: {player}
Tipo: {mode}
Acción: {action}

{memory_context}

Responde narrativamente como Dungeon Master, siguiendo las instrucciones del sistema.
"""

    try:
        # ============================================================
        # 🔮 Llamada moderna a GPT-5
        # ============================================================
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.85,
            max_completion_tokens=400,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"S.A.M. hace una pausa incómoda... (Error interno del narrador: {e})"
