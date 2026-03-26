import os
import json
import time
from typing import List, Dict

import requests
from upstash_vector import Index

# Constants and environment config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "foods.json")
UPSTASH_VECTOR_REST_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_VECTOR_REST_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
UPSTASH_VECTOR_MODEL = os.getenv("UPSTASH_VECTOR_EMBEDDING_MODEL", "mixedbread-ai/mxbai-embed-large-v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
API_URL_BASE = os.getenv("OLLAMA_API_URL_BASE", "http://localhost:11434/v1")
LEGACY_API_URL_BASE = os.getenv("OLLAMA_LEGACY_API_URL_BASE", "http://localhost:11434/api")

if not UPSTASH_VECTOR_REST_URL or not UPSTASH_VECTOR_REST_TOKEN:
    raise RuntimeError("Missing UPSTASH_VECTOR_REST_URL or UPSTASH_VECTOR_REST_TOKEN in environment")

index = Index(url=UPSTASH_VECTOR_REST_URL, token=UPSTASH_VECTOR_REST_TOKEN)


def _retry(func, *args, retries=4, backoff=1, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            status = None
            if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
                status = exc.response.status_code
            if status and status in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(backoff * (2 ** (attempt - 1)))
                continue
            raise


def call_ollama(path: str, payload: Dict, timeout: int = 30) -> Dict:
    url = f"{API_URL_BASE}{path}"
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def generate_response(prompt: str) -> str:
    try:
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 300,
        }
        result = call_ollama("/chat/completions", payload)

        first = result.get("choices", [None])[0]
        if first:
            if "message" in first and "content" in first["message"]:
                return first["message"]["content"].strip()
            if "text" in first:
                return first["text"].strip()

        if "text" in result:
            return result["text"].strip()

        raise ValueError("Unexpected chat completion format")
    except Exception as exc:
        print(f"⚠️ Modern generate endpoint failed: {exc}")

    try:
        url = f"{LEGACY_API_URL_BASE}/generate"
        response = requests.post(url, json={"model": LLM_MODEL, "prompt": prompt, "stream": False}, timeout=60)
        response.raise_for_status()
        payload = response.json()

        if "response" in payload:
            return payload["response"].strip()
        if "completion" in payload:
            return payload["completion"].strip()
        raise ValueError("Unexpected legacy generate response")
    except Exception as exc:
        raise RuntimeError(f"Generate request failed: {exc}")


def _build_upstash_items(food_data: List[Dict]) -> List:
    items = []
    for item in food_data:
        enriched_text = item.get("text", "")
        if "region" in item:
            enriched_text += f" This food is popular in {item['region']} ."
        if "type" in item:
            enriched_text += f" It is a type of {item['type']} ."

        metadata = {k: v for k, v in item.items() if k not in ("id", "text")}
        # tuple format used by Upstash client: (id, text, metadata)
        items.append((item["id"], enriched_text, metadata))
    return items


def ingest_to_upstash(food_data: List[Dict], batch_size: int = 200):
    print(f"🔼 Upserting {len(food_data)} documents into Upstash Vector...")
    items = _build_upstash_items(food_data)

    for i in range(0, len(items), batch_size):
        chunk = items[i : i + batch_size]
        _retry(index.upsert, chunk)
    print("✅ Upsert complete")


def rag_query(question: str, top_k: int = 3) -> str:
    query_result = _retry(index.query, data=question, top_k=top_k, include_metadata=True)

    if isinstance(query_result, dict) and "result" in query_result:
        hits = query_result["result"]
    elif isinstance(query_result, list):
        hits = query_result
    else:
        raise ValueError("Unexpected query result structure")

    # Interpret hits based on known format
    docs = []
    for hit in hits[:top_k]:
        if isinstance(hit, dict):
            text_field = hit.get("text") or hit.get("document") or ""
            docs.append(text_field)
        else:
            docs.append(str(hit))

    if not docs:
        return "No results retrieved from vector store."

    context = "\n".join(docs)
    rag_prompt = f"""Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"""
    return generate_response(rag_prompt)


if __name__ == "__main__":
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        food_data = json.load(f)

    ingest_to_upstash(food_data)

    print("\n🧠 RAG is ready. Ask a question (type 'exit' to quit):\n")
    while True:
        question = input("You: ")
        if question.strip().lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        try:
            answer = rag_query(question)
            print("🤖:", answer)
        except Exception as exc:
            print("❌ Error during RAG query:", exc)
            print("Please confirm Upstash and Ollama services are reachable.")
