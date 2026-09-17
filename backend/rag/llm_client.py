import os
import json
from pathlib import Path
from typing import Dict, Any, List

import httpx

# Load the system prompt template
_PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "rag" / "prompts" / "report_prompt_template.md"

def _load_template() -> str:
    with open(_PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()

def _format_numeric_block(prediction: Dict[str, Any], audio_quality_score: float) -> str:
    # Expected keys: probability, confidence
    probability = prediction.get("probability") or prediction.get("confidence") or ""
    confidence = prediction.get("confidence") or prediction.get("probability") or ""
    return f"PROBABILITY: {probability}\nCONFIDENCE: {confidence}\nAUDIO_QUALITY_SCORE: {audio_quality_score}"

def assemble_prompt(
    prediction: Dict[str, Any],
    structured_evidence: Dict[str, Any],
    retrieved_chunks: List[Dict[str, Any]],
    similarity_results: List[Dict[str, Any]],
    audio_quality_score: float,
) -> str:
    """Insert all required fields into the prompt template.
    Returns the full prompt string ready for the Anthropic API.
    """
    template = _load_template()
    numeric_block = _format_numeric_block(prediction, audio_quality_score)
    # JSON‑serialize the structures for insertion (compact but readable)
    prediction_json = json.dumps(prediction, ensure_ascii=False, indent=2)
    structured_json = json.dumps(structured_evidence, ensure_ascii=False, indent=2)
    retrieved_json = json.dumps(retrieved_chunks, ensure_ascii=False, indent=2)
    similarity_json = json.dumps(similarity_results, ensure_ascii=False, indent=2)
    prompt = template.format(
        probability=prediction.get("probability", ""),
        confidence=prediction.get("confidence", ""),
        audio_quality_score=audio_quality_score,
        prediction_json=prediction_json,
        structured_evidence_json=structured_json,
        retrieved_chunks_json=retrieved_json,
        similarity_results_json=similarity_json,
    )
    # Replace the placeholder numeric block with the explicit block
    prompt = prompt.replace("[NUMERIC_VALUES]", numeric_block)
    return prompt

from backend.core.config import settings

def call_anthropic_api(prompt: str, model: str = "claude-3-opus-20240229") -> str:
    """Call the Anthropic API with a system prompt.
    Returns the raw content of the assistant's reply.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY") or getattr(settings, "ANTHROPIC_API_KEY", None)
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 1024,
        "system": prompt,
        "messages": [{"role": "user", "content": "Generate the report according to the above instructions."}],
    }
    response = httpx.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    # Anthropic returns a list of content blocks; concatenate text parts
    content = "".join(block.get("text", "") for block in data.get("content", []))
    return content

import time
from backend.core.logging import log_llm_report_metrics

def generate_report(
    prediction: Dict[str, Any],
    structured_evidence: Dict[str, Any],
    retrieved_chunks: List[Dict[str, Any]],
    similarity_results: List[Dict[str, Any]],
    audio_quality_score: float,
    session_id: str = "session_llm",
    model: str = "claude-3-opus-20240229",
) -> str:
    """High‑level helper that assembles the prompt and calls the LLM.
    Returns the final report string and logs execution diagnostics.
    """
    start_time = time.perf_counter()
    prompt = assemble_prompt(
        prediction, structured_evidence, retrieved_chunks, similarity_results, audio_quality_score
    )
    report_text = call_anthropic_api(prompt, model=model)
    duration_ms = (time.perf_counter() - start_time) * 1000.0

    log_llm_report_metrics(
        session_id=session_id,
        model=model,
        latency_ms=duration_ms,
        validation_status="GENERATED",
    )

    return report_text
