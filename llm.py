import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"


def call_llm(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()
    return response.json()["response"]


def extract_json(text):
    """
    Extract first JSON object from model response
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group()
    return None


def insurance_decoder(text):
    prompt = f"""
You are analyzing an INDIAN HEALTH INSURANCE POLICY.

STRICT RULES:
- Extract ONLY information explicitly present in the document.
- DO NOT invent diseases or treatments.
- DO NOT mention suicide, mental health, or self-harm unless written.
- If data is missing, return empty list [].
- Every risk MUST include financial impact explanation.

Return ONLY VALID JSON.

JSON FORMAT:

{{
 "risk_score": number between 0 and 100,

 "waiting_periods":[
   {{
     "condition":"disease or treatment name",
     "duration":"waiting period in months",
     "impact":"Explain financial consequence in simple Indian family terms"
   }}
 ],

 "exclusions":[
   {{
     "item":"treatment not covered",
     "impact":"Explain why claim may be rejected and cost burden"
   }}
 ],

 "co_payment":[
   {{
     "percentage":"co-payment percentage",
     "impact":"Explain how much user may pay from pocket"
   }}
 ],

 "hidden_limits":[
   {{
     "limit":"coverage cap or sub-limit",
     "impact":"Explain financial loss if hospital bill exceeds this"
   }}
 ],

 "danger_alerts":[
   {{
     "severity":"Critical/High/Medium",
     "message":"Simple warning like: Your diabetes treatment won't be covered for 36 months"
   }}
 ]
}}

Pay SPECIAL attention to detecting:
- waiting period
- exclusions
- not covered clauses
- shall not be liable
- sub-limits
- co-payment
- room rent limits

Policy Text:
{text}
"""

    raw_output = call_llm(prompt)

    json_string = extract_json(raw_output)

    if not json_string:
        print("RAW MODEL OUTPUT:\n", raw_output)
        return None

    try:
        return json.loads(json_string)
    except:
        print("JSON PARSE FAILED:\n", raw_output)
        return None