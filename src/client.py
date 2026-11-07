"""Thin async client for the Adaption inference API (OpenAI-Responses-style)."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = "https://api.prod.adaptionlabs.ai/api/v1"


def load_env() -> None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


load_env()


class ModelClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("ADAPTION_API_KEY")
        if not self.api_key:
            raise RuntimeError("ADAPTION_API_KEY is not set — copy .env.example to .env and fill it in")
        self.base_url = (base_url or os.environ.get("ADAPTION_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self._http = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=httpx.Timeout(120.0, connect=30.0),
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def list_models(self) -> list[dict]:
        r = await self._http.get(f"{self.base_url}/models", params={"type": "hosted"})
        if r.status_code != 200:
            raise RuntimeError(f"models list failed {r.status_code}: {r.text[:500]}")
        return r.json().get("data", [])

    async def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 5000,
        temperature: float = 1.0,
    ) -> str:
        """messages: [{'role': 'user'|'assistant', 'content': str}, ...]"""
        payload = {
            "model": model,
            "instructions": system,
            "input": [
                {"role": m["role"], "content": m["content"]}
                for m in messages
            ],
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        for attempt in range(3):
            try:
                r = await self._http.post(f"{self.base_url}/responses", json=payload)
            except httpx.HTTPError as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(2**attempt)
                continue
            if r.status_code == 200:
                return self._extract_text(r.json())
            if r.status_code in (429, 500, 502, 503) and attempt < 2:
                await asyncio.sleep(2**attempt * 2)
                continue
            raise RuntimeError(f"responses call failed {r.status_code}: {r.text[:800]}")
        raise RuntimeError("unreachable")

    @staticmethod
    def _extract_text(data: dict) -> str:
        # reasoning models may leave output_text empty when the token budget
        # is consumed by reasoning; prefer the first non-empty content part
        candidates = []
        if isinstance(data.get("output_text"), str):
            candidates.append(data["output_text"])
        for item in data.get("output") or []:
            if item.get("type") == "message":
                for part in item.get("content") or []:
                    if part.get("type") in ("output_text", "text") and isinstance(part.get("text"), str):
                        candidates.append(part["text"])
        if isinstance(data.get("choices"), list) and data["choices"]:
            msg = data["choices"][0].get("message", {})
            if isinstance(msg.get("content"), str):
                candidates.append(msg["content"])
        for c in candidates:
            if c.strip():
                return c
        if candidates:
            return candidates[0]
        raise RuntimeError(f"could not extract text from response keys={list(data)[:10]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", action="store_true", help="list models granted to this key")
    ap.add_argument("--ping", metavar="MODEL", help="one tiny completion to verify the pipeline")
    args = ap.parse_args()

    async def run() -> None:
        client = ModelClient()
        try:
            if args.models:
                models = await client.list_models()
                print(json.dumps(models, indent=2)[:6000])
            if args.ping:
                text = await client.complete(
                    args.ping, "Reply concisely.",
                    [{"role": "user", "content": "Say 'pong' and nothing else."}],
                    max_tokens=512, temperature=0.0,
                )
                print(repr(text))
        finally:
            await client.close()

    asyncio.run(run())


if __name__ == "__main__":
    main()
    sys.exit(0)
