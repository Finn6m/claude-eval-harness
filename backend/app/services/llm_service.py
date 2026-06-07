import os
import httpx
import json

# created call_model and call_judge. call_model generates a response from the model based on the user prompt
# call_judge sends the response from call_model to claude and returns the verdict on whether the prompt
# passed or failed, along with a confidence score. call_model can use whatever temperature the user selcects
# where as call_judge always uses a temperature of 0.1 in order to be consistent and as deterministic as possible.

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_BASE = "https://api.anthropic.com/v1/messages"

async def call_model(prompt: str, model: str, temperature: float = 0.7) -> str:
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 1024,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(ANTHROPIC_BASE, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]
    
async def call_judge(
    original_prompt: str,
    model_output: str,
    judge_instruction: str,
    judge_model: str = "claude-haiku-4-5-20251001",
) -> dict:
    judge_prompt = f"""You are an expert evaluator for LLM outputs.

ORIGINAL PROMPT:
{original_prompt}

MODEL OUTPUT:
{model_output}

EVALUATION CRITERIA:
{judge_instruction}

Respond ONLY in this exact JSON format, no other text:
{{
  "is_failure": true or false,
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence explanation"
}}

Be calibrated. If you are genuinely unsure, reflect that with a lower confidence score below 0.7."""

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": judge_model,
        "max_tokens": 256,
        "temperature": 0.1,
        "messages": [{"role": "user", "content": judge_prompt}],
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(ANTHROPIC_BASE, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        text = data["content"][0]["text"].strip()
        try:
            return json.loads(text)
        except Exception:
            return {"is_failure": False, "confidence": 0.3, "reasoning": "Judge parse error"}