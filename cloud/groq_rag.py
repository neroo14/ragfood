"""
🚀 RAG System with Groq Cloud API & Upstash Vector

Migration from local Ollama LLM to Groq Cloud API.
Maintains Upstash Vector for embeddings and semantic search.

Features:
- Cloud-based LLM inference via Groq
- Exponential backoff retry logic
- Usage tracking and cost estimation
- Comprehensive error handling
- Detailed logging for debugging
- Fallback to caching for resilience

Environment Variables Required:
- UPSTASH_VECTOR_REST_URL: Vector database URL
- UPSTASH_VECTOR_REST_TOKEN: Vector database token
- GROQ_API_KEY: Groq API authentication key
- GROQ_MODEL: Model to use (default: llama-3.1-8b-instant)
- GROQ_MAX_TOKENS: Max tokens per response (default: 1024)
- GROQ_TEMPERATURE: Sampling temperature (default: 0.7)
"""

import os
import json
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime

import requests
from upstash_vector import Index
from groq import Groq, APIError, RateLimitError, APIConnectionError

# ============================================================================
# Configuration & Environment Setup
# ============================================================================

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Directory and file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "../ragfood/foods.json")
CACHE_FILE = os.path.join(BASE_DIR, ".query_cache.json")

# Upstash Vector Configuration
UPSTASH_VECTOR_REST_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_VECTOR_REST_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
UPSTASH_VECTOR_MODEL = os.getenv("UPSTASH_VECTOR_EMBEDDING_MODEL", "mixedbread-ai/mxbai-embed-large-v1")

if not UPSTASH_VECTOR_REST_URL or not UPSTASH_VECTOR_REST_TOKEN:
    raise RuntimeError(
        "❌ Missing Upstash Vector credentials. "
        "Set UPSTASH_VECTOR_REST_URL and UPSTASH_VECTOR_REST_TOKEN in .env"
    )

# Initialize Upstash Vector client
upstash_index = Index(url=UPSTASH_VECTOR_REST_URL, token=UPSTASH_VECTOR_REST_TOKEN)
logger.info("✅ Upstash Vector client initialized")

# Groq Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "❌ Missing GROQ_API_KEY. "
        "Add GROQ_API_KEY to .env file"
    )

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)
logger.info("✅ Groq client initialized")

# Model and generation parameters
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
GROQ_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "30"))
GROQ_RETRIES = int(os.getenv("GROQ_RETRIES", "3"))

# ============================================================================
# Usage Tracking & Cost Estimation
# ============================================================================

class UsageTracker:
    """Track API usage and estimate costs."""
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_calls = 0
        self.failed_calls = 0
        self.cached_calls = 0
        
        # Groq pricing (approximate, in USD per token)
        self.input_token_cost = 0.0005 / 1_000_000  # $0.5 per 1M tokens
        self.output_token_cost = 0.0015 / 1_000_000  # $1.5 per 1M tokens
    
    def add(self, input_tokens: int, output_tokens: int, failed: bool = False, cached: bool = False):
        """Record API usage."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_calls += 1
        if failed:
            self.failed_calls += 1
        if cached:
            self.cached_calls += 1
    
    def get_estimated_cost(self) -> float:
        """Calculate estimated cost in USD."""
        return (self.total_input_tokens * self.input_token_cost +
                self.total_output_tokens * self.output_token_cost)
    
    def get_stats(self) -> Dict:
        """Get usage statistics."""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.total_calls - self.failed_calls,
            "failed_calls": self.failed_calls,
            "cached_calls": self.cached_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "estimated_cost_usd": f"${self.get_estimated_cost():.4f}",
            "timestamp": datetime.now().isoformat()
        }

usage_tracker = UsageTracker()

# ============================================================================
# Query Caching
# ============================================================================

class QueryCache:
    """Simple file-based cache for query results."""
    
    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ Failed to save cache: {e}")
    
    def get(self, question: str) -> Optional[str]:
        """Retrieve cached answer."""
        return self.cache.get(question.lower())
    
    def set(self, question: str, answer: str):
        """Cache answer for question."""
        self.cache[question.lower()] = answer
        self._save_cache()
    
    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        self._save_cache()

query_cache = QueryCache()

# ============================================================================
# Retry Logic & Error Handling
# ============================================================================

def retry_with_backoff(func, *args, retries=GROQ_RETRIES, backoff=1, **kwargs):
    """
    Retry function with exponential backoff.
    
    Handles:
    - Rate limit errors (429)
    - Server errors (500-503)
    - Connection errors
    - Timeout errors
    """
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            if attempt < retries:
                wait_time = backoff * (2 ** (attempt - 1))
                logger.warning(f"⏱️ Rate limited. Retrying in {wait_time}s (attempt {attempt}/{retries})")
                time.sleep(wait_time)
                continue
            logger.error(f"❌ Rate limit exceeded after {retries} retries")
            raise
        except APIConnectionError as e:
            if attempt < retries:
                wait_time = backoff * (2 ** (attempt - 1))
                logger.warning(f"🔌 Connection error. Retrying in {wait_time}s (attempt {attempt}/{retries})")
                time.sleep(wait_time)
                continue
            logger.error(f"❌ Connection failed after {retries} retries")
            raise
        except APIError as e:
            if e.status_code and e.status_code >= 500 and attempt < retries:
                wait_time = backoff * (2 ** (attempt - 1))
                logger.warning(f"⚠️ Server error {e.status_code}. Retrying in {wait_time}s (attempt {attempt}/{retries})")
                time.sleep(wait_time)
                continue
            logger.error(f"❌ API error: {e}")
            raise

# ============================================================================
# Vector Store Operations
# ============================================================================

def _build_upstash_items(food_data: List[Dict]) -> List:
    """Prepare food items for Upstash Vector ingestion."""
    items = []
    for item in food_data:
        enriched_text = item.get("text", "")
        if "region" in item:
            enriched_text += f" This food is popular in {item['region']}."
        if "type" in item:
            enriched_text += f" It is a type of {item['type']}."
        
        metadata = {k: v for k, v in item.items() if k not in ("id", "text")}
        items.append((item["id"], enriched_text, metadata))
    return items

def ingest_to_upstash(food_data: List[Dict], batch_size: int = 200):
    """Ingest food data into Upstash Vector."""
    logger.info(f"🔼 Upserting {len(food_data)} documents into Upstash Vector...")
    items = _build_upstash_items(food_data)
    
    for i in range(0, len(items), batch_size):
        chunk = items[i : i + batch_size]
        try:
            retry_with_backoff(upstash_index.upsert, chunk)
            logger.info(f"   ✅ Batch {i//batch_size + 1} uploaded")
        except Exception as e:
            logger.error(f"❌ Failed to upsert batch: {e}")
            raise
    
    logger.info("✅ Upstash ingestion complete")

def retrieve_context(question: str, top_k: int = 3) -> List[str]:
    """Retrieve relevant documents from vector store using semantic search."""
    try:
        query_result = retry_with_backoff(upstash_index.query, data=question, top_k=top_k, include_metadata=True)
        
        if isinstance(query_result, dict) and "result" in query_result:
            hits = query_result["result"]
        elif isinstance(query_result, list):
            hits = query_result
        else:
            logger.warning(f"⚠️ Unexpected query result: {type(query_result)}")
            return []
        
        docs = []
        for hit in hits[:top_k]:
            if isinstance(hit, dict):
                text_field = hit.get("text") or hit.get("document") or ""
                score = hit.get("score", 0)
                docs.append(text_field)
                logger.debug(f"   Retrieved: {text_field[:50]}... (score: {score:.3f})")
            else:
                docs.append(str(hit))
        
        logger.info(f"✓ Retrieved {len(docs)} relevant documents")
        return docs
    except Exception as e:
        logger.error(f"❌ Vector search failed: {e}")
        return []

# ============================================================================
# LLM Generation with Groq
# ============================================================================

def generate_response(prompt: str) -> str:
    """
    Generate response using Groq API with full error handling and retries.
    
    Args:
        prompt: The prompt to send to the LLM
    
    Returns:
        Generated response text
    
    Raises:
        RuntimeError: If all retries exhausted
    """
    logger.debug(f"🤖 Generating response with Groq ({GROQ_MODEL})...")
    
    message_payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant with expertise in food, nutrition, and culinary topics."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": GROQ_TEMPERATURE,
        "max_tokens": GROQ_MAX_TOKENS,
        "top_p": 1,
        "stream": False,
        "stop": None
    }
    
    try:
        def _create_completion():
            return groq_client.chat.completions.create(**message_payload)
        
        # Call with retry logic
        completion = retry_with_backoff(_create_completion, retries=GROQ_RETRIES)
        
        # Extract content from response
        if completion.choices and len(completion.choices) > 0:
            content = completion.choices[0].message.content.strip()
            
            # Track usage
            if hasattr(completion, 'usage'):
                usage_tracker.add(
                    input_tokens=completion.usage.prompt_tokens,
                    output_tokens=completion.usage.completion_tokens
                )
                logger.debug(
                    f"📊 Tokens - Input: {completion.usage.prompt_tokens}, "
                    f"Output: {completion.usage.completion_tokens}"
                )
            
            logger.info("✅ Response generated successfully")
            return content
        
        raise ValueError("Empty response from Groq API")
    
    except RateLimitError:
        logger.error("❌ Rate limit exceeded. Consider adding delays between requests.")
        usage_tracker.add(0, 0, failed=True)
        raise RuntimeError("Groq API rate limit exceeded. Please try again later.")
    except APIConnectionError:
        logger.error("❌ Connection to Groq API failed. Check your network and GROQ_API_KEY.")
        usage_tracker.add(0, 0, failed=True)
        raise RuntimeError("Could not connect to Groq API. Please check your connection.")
    except APIError as e:
        logger.error(f"❌ Groq API error: {e}")
        usage_tracker.add(0, 0, failed=True)
        raise RuntimeError(f"Groq API returned error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error during generation: {e}")
        usage_tracker.add(0, 0, failed=True)
        raise

# ============================================================================
# RAG Pipeline
# ============================================================================

def rag_query(question: str, use_cache: bool = True, top_k: int = 3) -> str:
    """
    Execute RAG query: retrieve context + generate answer.
    
    Args:
        question: User's question
        use_cache: Whether to use cached answers
        top_k: Number of documents to retrieve
    
    Returns:
        Generated answer based on retrieved context
    """
    logger.info(f"❓ Processing question: {question}")
    
    # Check cache first
    if use_cache:
        cached_answer = query_cache.get(question)
        if cached_answer:
            logger.info("✓ Returning cached answer")
            usage_tracker.add(0, 0, cached=True)
            return cached_answer
    
    # Retrieve context from vector store
    logger.info("🔍 Retrieving relevant context...")
    docs = retrieve_context(question, top_k=top_k)
    
    if not docs:
        logger.warning("⚠️ No relevant documents found in vector store")
        return "Sorry, I couldn't find relevant information in the database to answer your question."
    
    # Build RAG prompt
    context = "\n".join(docs)
    rag_prompt = f"""You are a helpful assistant answering questions about food and cuisine.

Use ONLY the following context to answer the question. If the answer is not in the context, say "I don't have that information in my database."

Context:
{context}

Question: {question}

Answer:"""
    
    # Generate response
    logger.info("🧠 Generating answer with Groq...")
    try:
        answer = generate_response(rag_prompt)
        
        # Cache successful answer
        if use_cache:
            query_cache.set(question, answer)
        
        logger.info("✅ Query completed successfully")
        return answer
    
    except Exception as e:
        logger.error(f"❌ Failed to generate response: {e}")
        raise

# ============================================================================
# Main Interactive Loop
# ============================================================================

def main():
    """Main interactive RAG interface."""
    print("\n" + "="*70)
    print("🧠 RAG System with Groq Cloud API & Upstash Vector")
    print("="*70)
    print(f"Model: {GROQ_MODEL}")
    print(f"Vector DB: Upstash ({UPSTASH_VECTOR_MODEL})")
    print("="*70 + "\n")
    
    # Load and ingest food data
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            food_data = json.load(f)
        logger.info(f"📚 Loaded {len(food_data)} food items")
        ingest_to_upstash(food_data)
    except FileNotFoundError:
        logger.error(f"❌ Food data file not found: {JSON_FILE}")
        return
    except Exception as e:
        logger.error(f"❌ Failed to load/ingest data: {e}")
        return
    
    # Interactive query loop
    print("💬 Ask a question (type 'exit' to quit, 'stats' for usage, 'clear' to clear cache):\n")
    
    while True:
        try:
            question = input("You: ").strip()
            
            if not question:
                continue
            
            if question.lower() == "exit":
                print("\n👋 Goodbye!")
                print("\n📊 Final Usage Statistics:")
                print(json.dumps(usage_tracker.get_stats(), indent=2))
                break
            
            if question.lower() == "stats":
                print("\n📊 Current Usage Statistics:")
                print(json.dumps(usage_tracker.get_stats(), indent=2))
                print()
                continue
            
            if question.lower() == "clear":
                query_cache.clear()
                print("✓ Cache cleared\n")
                continue
            
            # Process query
            answer = rag_query(question)
            print(f"\n🤖: {answer}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            print(f"❌ Error: {str(e)}\n")

if __name__ == "__main__":
    main()