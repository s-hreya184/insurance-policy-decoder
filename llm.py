"""
llm.py — LLM calls via Groq API (replaces Ollama)
Model: llama3-8b-8192 (free, fast, good for structured extraction)
"""

import json
import re
import streamlit as st
from groq import Groq

# ── Client ─────────────────────────────────────────────────────────────────────

def _client() -> Groq:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise RuntimeError(
            "GROQ_API_KEY not found. Add it to .streamlit/secrets.toml locally "
            "or to the Secrets section in Streamlit Cloud."
        )
    return Groq(api_key=api_key)


MAX_SINGLE = 6000
MODEL      = "llama-3.1-8b-instant"   # free tier; swap to llama-3.3-70b-versatile for better quality


def call_llm(prompt: str, timeout: int = 180) -> str:
    """Send a prompt to Groq and return the response string."""
    try:
        response = _client().chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.05,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Groq LLM call failed: {e}")


# ── JSON extractor (unchanged) ─────────────────────────────────────────────────

def extract_json(text: str) -> str | None:
    clean = re.sub(r"```(?:json)?", "", text).strip()
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        candidate = match.group()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass
    for i, ch in enumerate(clean):
        if ch == "{":
            for j in range(len(clean), i, -1):
                try:
                    json.loads(clean[i:j])
                    return clean[i:j]
                except json.JSONDecodeError:
                    continue
    return None


# ── Prompt (unchanged from original) ──────────────────────────────────────────

_EXTRACTION_PROMPT = """You are a strict Indian health insurance policy analyzer.

TASK: Extract ONLY information explicitly present in the policy clauses below.
These clauses have already been pre-filtered from a full policy document to contain
only the sections relevant to exclusions, waiting periods, co-payments, and limits.

RULES:
- Extract ONLY what is explicitly written. Do NOT invent or infer.
- Return empty lists [] when a category has no matches in the text.
- DO NOT mention suicide, self-harm, or mental health unless explicitly written.
- Every item must be traceable to an actual sentence in the text.

RISK SCORE GUIDE (0–100):
  0–30  : Few exclusions, short waiting periods, low co-pay — policy is claimant-friendly
  31–60 : Moderate exclusions or waiting periods — some financial exposure
  61–80 : Many exclusions, long waiting periods, or high co-pay — significant risk
  81–100: Extensive exclusions, multiple co-pays, very long waiting periods — high rejection risk

OUTPUT: Respond with ONLY a valid JSON object. No preamble, no explanation, no markdown fences.

{{
  "risk_score": <integer 0-100>,
  "waiting_periods": [
    {{"condition": "<name>", "duration": "<e.g. 2 years>", "impact": "<plain English consequence>"}}
  ],
  "exclusions": [
    {{"item": "<excluded item>", "impact": "<what the policyholder must pay themselves>"}}
  ],
  "co_payment": [
    {{"percentage": "<e.g. 20%>", "condition": "<when it applies>", "impact": "<cost consequence>"}}
  ],
  "hidden_limits": [
    {{"limit": "<description>", "applies_to": "<treatment or scenario>", "impact": "<consequence>"}}
  ],
  "danger_alerts": [
    {{"severity": "<Critical|High|Medium>", "message": "<plain language warning>"}}
  ]
}}

Policy Clauses:
{text}
"""


def _parse_result(raw: str) -> dict | None:
    json_string = extract_json(raw)
    if not json_string:
        return None
    try:
        parsed = json.loads(json_string)
        defaults = {
            "risk_score": 0,
            "waiting_periods": [],
            "exclusions": [],
            "co_payment": [],
            "hidden_limits": [],
            "danger_alerts": [],
        }
        defaults.update(parsed)
        defaults["risk_score"] = max(0, min(100, int(defaults["risk_score"])))
        return defaults
    except (json.JSONDecodeError, ValueError):
        return None


def _merge_results(a: dict, b: dict) -> dict:
    return {
        "risk_score":      max(a.get("risk_score", 0), b.get("risk_score", 0)),
        "waiting_periods": a.get("waiting_periods", []) + b.get("waiting_periods", []),
        "exclusions":      a.get("exclusions", [])      + b.get("exclusions", []),
        "co_payment":      a.get("co_payment", [])      + b.get("co_payment", []),
        "hidden_limits":   a.get("hidden_limits", [])   + b.get("hidden_limits", []),
        "danger_alerts":   a.get("danger_alerts", [])   + b.get("danger_alerts", []),
    }


def insurance_decoder(filtered_text: str) -> dict | None:
    text = filtered_text.strip()
    if not text:
        return None

    if len(text) <= MAX_SINGLE:
        raw = call_llm(_EXTRACTION_PROMPT.format(text=text))
        return _parse_result(raw)
    else:
        mid      = len(text) // 2
        split_at = text.rfind("\n\n", mid - 500, mid + 500)
        if split_at == -1:
            split_at = text.rfind("\n", mid - 200, mid + 200)
        if split_at == -1:
            split_at = mid

        part_a = text[:split_at].strip()
        part_b = text[split_at:].strip()

        result_a = _parse_result(call_llm(_EXTRACTION_PROMPT.format(text=part_a))) or {}
        result_b = _parse_result(call_llm(_EXTRACTION_PROMPT.format(text=part_b))) or {}

        if not result_a and not result_b:
            return None
        if not result_a:
            return result_b
        if not result_b:
            return result_a
        return _merge_results(result_a, result_b)