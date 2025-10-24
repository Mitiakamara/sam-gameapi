import json
import os
import random
from typing import Optional

# ============================================================
# 🎭 TONE ADAPTER 5.2b
# ------------------------------------------------------------
# Lee /data/emotion/emotional_scale.json y aplica el tono
# narrativo correspondiente a la emoción o tipo de escena.
# ============================================================

# Ruta por defecto al archivo de escala emocional
EMOTIONAL_SCALE_PATH = os.getenv(
    "EMOTIONAL_SCALE_PATH",
    "data/emotion/emotional_scale.json"
)

# Cargar archivo JSON
def load_emotional_scale(path: str = EMOTIONAL_SCALE_PATH) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ToneAdapter] ⚠️ Error al cargar emotional_scale.json: {e}")
        return {}

# Objeto global con la escala cargada
EMOTIONAL_SCALE = load_emotional_scale()

# ------------------------------------------------------------
# 🔍 Funciones auxiliares
# ------------------------------------------------------------

def get_emotion_for_scene(scene_type: str) -> str:
    """Devuelve la emoción predeterminada para un tipo de escena."""
    return EMOTIONAL_SCALE.get("scene_adaptation", {}).get(scene_type, "neutral")


def get_tone_data(emotion: str) -> dict:
    """Devuelve el bloque de datos del tono para una emoción."""
    return EMOTIONAL_SCALE.get("emotions", {}).get(emotion, {})


def get_random_bias_words(emotion: str, n: int = 2) -> list[str]:
    """Selecciona algunas palabras de vocabulario característico del tono."""
    tone_data = get_tone_data(emotion)
    vocab = tone_data.get("vocabulary_bias", [])
    return random.sample(vocab, min(n, len(vocab))) if vocab else []


# ------------------------------------------------------------
# ✨ Función principal
# ------------------------------------------------------------

def apply_tone(scene_type: str, base_text: str, intensity: int = 3) -> str:
    """
    Aplica el tono narrativo adaptativo según la emoción de la escena.
    
    - scene_type: tipo de escena (combat, exploration, revelation, etc.)
    - base_text: texto base generado por el renderer o narrador
    - intensity: nivel de 1 a 5 (por defecto 3)
    """

    emotion = get_emotion_for_scene(scene_type)
    tone_data = get_tone_data(emotion)

    if not tone_data:
        return base_text

    tone = tone_data.get("tone", "")
    style = tone_data.get("style", "")
    bias_words = get_random_bias_words(emotion, n=2)

    # Adaptación simple de tono (versión conceptual)
    adapted_text = base_text.strip()

    # 1️⃣ Ajuste de puntuación según intensidad
    if intensity >= 4:
        adapted_text = adapted_text.replace(".", "...")
    if intensity == 5:
        adapted_text = f"**{adapted_text.upper()}**"

    # 2️⃣ Inserción contextual de palabras de sesgo emocional
    if bias_words:
        adapted_text += f" ({', '.join(bias_words)})"

    # 3️⃣ Prefijo narrativo según tono general
    prefix = ""
    if intensity >= 3:
        prefix = f"[{tone}] "

    # 4️⃣ Resultado final
    result = f"{prefix}{adapted_text}"
    return result


# ------------------------------------------------------------
# 🧪 Modo de prueba
# ------------------------------------------------------------

if __name__ == "__main__":
    demo_scenes = ["exploration", "combat", "rest", "revelation", "defeat", "victory"]
    for s in demo_scenes:
        text = "El grupo avanza por el sendero nevado."
        out = apply_tone(s, text, intensity=random.randint(2, 5))
        print(f"\nScene: {s}\n{out}")
