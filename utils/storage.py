import json
import os
from typing import Any, Dict

BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data")

def _ensure_data_folder():
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

def _get_path(filename: str) -> str:
    _ensure_data_folder()
    return os.path.join(BASE_PATH, filename)

def read_json(filename: str) -> Dict[str, Any]:
    path = _get_path(filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def write_json(filename: str, data: Dict[str, Any]) -> None:
    path = _get_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
