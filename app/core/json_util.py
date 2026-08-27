import json
import re
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("condigence.core.json_util")


def extract_json_from_llm(content: str) -> Optional[Dict[str, Any]]:
    """
    Extracts and parses JSON from LLM output, handling:
    - Markdown code fences (```json ... ``` or ``` ... ```)
    - Reasoning tags like <think>...</think>
    - Preamble / conversational chatter before or after JSON
    """
    if not content:
        return None

    cleaned = content.strip()

    # 1. Remove <think>...</think> blocks from reasoning models
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL).strip()

    # 2. Extract from markdown code fence if present
    if "```json" in cleaned:
        try:
            block = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
            return json.loads(block)
        except Exception:
            pass

    if "```" in cleaned:
        try:
            block = cleaned.split("```", 1)[1].split("```", 1)[0].strip()
            return json.loads(block)
        except Exception:
            pass

    # 3. Direct JSON load attempt
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 4. Regex search for outermost JSON object { ... }
    match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except Exception:
            pass

    return None
