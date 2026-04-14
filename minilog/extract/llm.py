"""LLM bridge for Anthropic API — thin wrapper with auth, retry, and parsing."""

import json
import os
import time

from minilog.extract.errors import DownloadError


DEFAULT_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 3
RETRY_DELAY = 2.0


def _get_client():
    """Create an Anthropic client from environment."""
    try:
        import anthropic
    except ImportError:
        raise DownloadError("llm", "anthropic SDK not installed: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise DownloadError("llm", "ANTHROPIC_API_KEY environment variable not set")

    return anthropic.Anthropic(api_key=api_key)


def call_llm(
    prompt: str,
    system: str = "",
    model: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.0,
) -> str:
    """Call the Anthropic API and return the text response.

    Retries on transient errors up to MAX_RETRIES times.
    """
    client = _get_client()
    model = model or os.environ.get("MINILOG_LLM_MODEL", DEFAULT_MODEL)

    messages = [{"role": "user", "content": prompt}]

    for attempt in range(MAX_RETRIES):
        try:
            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
            }
            if system:
                kwargs["system"] = system

            response = client.messages.create(**kwargs)
            return response.content[0].text

        except Exception as e:
            error_str = str(e)
            # Retry on rate limits and server errors
            if attempt < MAX_RETRIES - 1 and ("rate" in error_str.lower() or "529" in error_str or "500" in error_str):
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise DownloadError("llm", f"API call failed after {attempt + 1} attempts: {e}")


def call_llm_json(
    prompt: str,
    system: str = "",
    model: str | None = None,
    max_tokens: int = 4096,
) -> dict | list:
    """Call LLM and parse the response as JSON."""
    raw = call_llm(prompt, system=system, model=model, max_tokens=max_tokens)

    # Try to extract JSON from the response (may be wrapped in ```json...```)
    text = raw.strip()
    if text.startswith("```"):
        # Remove code fence
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise DownloadError("llm", f"Failed to parse LLM response as JSON: {e}\nRaw response:\n{raw[:500]}")
