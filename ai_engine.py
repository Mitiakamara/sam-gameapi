# sam-gameapi/ai_engine.py
import os
from openai import OpenAI

# ================================================================
# 🤖 CONFIGURACIÓN DE CLIENTE OPENAI
# ================================================================
# La API Key debe estar en tu entorno o variables de Render
# Ejemplo en .env: OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================================================================
# 🎭 PROMPT DEL SISTEMA (S.A.M. v3)
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
# 🧩 FUNCIÓN PRINCIPAL
# ================================================================
async def interpret_action(player: str, action: str, mode: str, context: dict | None = None) -> str:
    """
    Envía la acción o diálogo del jugador a GPT-5 y devuelve la respuesta narrativa.
    - player: nombre del jugador
    - action: texto libre (ej: "quiero escalar la pared")
    - mode: 'action' o 'dialogue'
    - context: información opcional del estado de la escena
    """

    # Preparar contexto adicional
    context_text = ""
    if context:
        try:
            # Formatear el contexto de manera legible
            scene = context.get("scene", "Escena desconocida")
            desc = context.get("description", "Sin detalles adicionales.")
            context_text = f"Escena actual: {scene}\nDescripción: {desc}\n"
        except Exception:
            context_text = ""

    # Prompt de usuario con toda la información relevante
    user_prompt = f"""
Jugador: {player}
Tipo: {mode}
Acción: {action}

{context_text}

Responde narrativamente como Dungeon Master, siguiendo las instrucciones del sistema.
"""

    try:
        # ============================================================
        # 🔮 Llamada a GPT-5
        # ============================================================
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.85,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        # Manejo seguro de errores
        return f"S.A.M. hace una pausa incómoda... (Error interno del narrador: {e})"
