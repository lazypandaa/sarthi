"""
Hindsight Client Layer
Wraps the official hindsight-client SDK with strict error boundaries,
credential masking, timeouts, and graceful fallbacks.
"""

import logging
from typing import Any, Dict, List, Optional

from .config import HindsightConfig

logger = logging.getLogger("gramvaani.hindsight.client")


class HindsightClient:
    """
    Low-level interface for Hindsight memory operations.
    Handles network errors, authentication issues, and SDK quirks gracefully.
    """

    def __init__(self, config: HindsightConfig):
        self.config = config
        self._raw_client = None
        self._init_client()

    def _init_client(self):
        """Attempts to initialize the raw Hindsight SDK client if configured."""
        if not self.config.is_configured:
            logger.info("Hindsight is not configured (API key or base URL missing). Operating in disabled fallback mode.")
            self._raw_client = None
            return

        try:
            from hindsight_client import Hindsight
            self._raw_client = Hindsight(
                base_url=self.config.base_url,
                api_key=self.config.api_key,
                timeout=self.config.timeout_seconds,
                max_attempts=self.config.max_retries,
            )
            logger.info(f"Hindsight client initialized (base_url: {self.config.base_url}, bank_id: {self.config.bank_id})")
        except Exception as e:
            logger.error(f"Failed to initialize Hindsight SDK client: {e}")
            self._raw_client = None

    @property
    def is_available(self) -> bool:
        """Returns True if the client was initialized with valid credentials."""
        return self._raw_client is not None

    def close(self):
        """Cleanly closes underlying client sessions."""
        if self._raw_client is not None:
            try:
                if hasattr(self._raw_client, "close"):
                    self._raw_client.close()
            except Exception as e:
                logger.debug(f"Error closing raw Hindsight client session: {e}")

    def _run_coro(self, coro_fn, sync_fn):
        """
        Executes an operation safely. If an asyncio event loop is currently active (e.g. inside
        FastAPI / uvicorn async handlers), runs coro_fn() in a dedicated worker thread with
        its own event loop to prevent 'RuntimeError: This event loop is already running'.
        If no event loop is running, invokes sync_fn() directly.
        """
        import asyncio
        import concurrent.futures

        try:
            asyncio.get_running_loop()
            in_loop = True
        except RuntimeError:
            in_loop = False

        if not in_loop:
            return sync_fn()

        def worker():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(coro_fn())
            finally:
                new_loop.close()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(worker).result()

    def health_check(self) -> Dict[str, Any]:
        """
        Check health/connectivity of Hindsight service without leaking credentials.
        Returns a structured dictionary status.
        """
        if not self.config.is_configured:
            return {
                "status": "unconfigured",
                "available": False,
                "message": "HINDSIGHT_API_KEY or HINDSIGHT_BASE_URL is not set.",
                "bank_id": self.config.bank_id,
            }

        if not self._raw_client:
            return {
                "status": "init_failed",
                "available": False,
                "message": "Hindsight SDK failed to initialize.",
                "bank_id": self.config.bank_id,
            }

        try:
            if hasattr(self._raw_client, "aget_version"):
                v = self._run_coro(
                    lambda: self._raw_client.aget_version(),
                    lambda: self._raw_client.get_version(),
                )
                if hasattr(v, "close") and callable(getattr(v, "close")):
                    v.close()
                    v = "mocked"
                return {"status": "healthy", "available": True, "version": str(v), "bank_id": self.config.bank_id}
            
            return {
                "status": "ready",
                "available": True,
                "bank_id": self.config.bank_id,
                "base_url": self.config.base_url,
            }
        except Exception as e:
            logger.warning(f"Hindsight health check warning: {e}")
            return {
                "status": "degraded",
                "available": False,
                "error": str(e),
                "bank_id": self.config.bank_id,
            }

    def retain(
        self,
        bank_id: str,
        content: str,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Retain a memory unit into Hindsight.
        Guarantees that errors never crash Gram Vaani.
        """
        if not self.is_available:
            logger.debug(f"Hindsight unavailable. Retain skipped for bank '{bank_id}'.")
            return {
                "success": False,
                "retained": False,
                "reason": "Hindsight is not configured or unavailable",
            }

        try:
            # Convert metadata values to strings as required by Hindsight SDK
            clean_metadata = {str(k): str(v) for k, v in (metadata or {}).items()}
            clean_tags = [str(t) for t in (tags or [])]

            response = self._run_coro(
                lambda: self._raw_client.aretain(
                    bank_id=bank_id,
                    content=content,
                    metadata=clean_metadata if clean_metadata else None,
                    tags=clean_tags if clean_tags else None,
                ),
                lambda: self._raw_client.retain(
                    bank_id=bank_id,
                    content=content,
                    metadata=clean_metadata if clean_metadata else None,
                    tags=clean_tags if clean_tags else None,
                ),
            )

            return {
                "success": True,
                "retained": True,
                "bank_id": bank_id,
                "items_count": getattr(response, "items_count", 1),
                "operation_id": getattr(response, "operation_id", None),
            }

        except Exception as e:
            logger.error(f"Hindsight retain error for bank '{bank_id}': {e}")
            return {
                "success": False,
                "retained": False,
                "error": str(e),
                "bank_id": bank_id,
            }

    def recall(
        self,
        bank_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        limit: int = 10,
        tags_match: str = "all",
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant memories from Hindsight.
        Returns a list of structured memory dicts. Never crashes on error.
        """
        if not self.is_available:
            logger.debug(f"Hindsight unavailable. Recall returning empty list for query '{query[:30]}'.")
            return []

        try:
            clean_tags = [str(t) for t in (tags or [])] if tags else None

            response = self._run_coro(
                lambda: self._raw_client.arecall(
                    bank_id=bank_id,
                    query=query,
                    tags=clean_tags,
                    tags_match=tags_match,
                    max_tokens=2048,
                    budget="mid",
                ),
                lambda: self._raw_client.recall(
                    bank_id=bank_id,
                    query=query,
                    tags=clean_tags,
                    tags_match=tags_match,
                    max_tokens=2048,
                    budget="mid",
                ),
            )

            raw_results = getattr(response, "results", None)
            if not raw_results:
                return []

            results: List[Dict[str, Any]] = []
            for item in raw_results[:limit]:
                results.append({
                    "id": getattr(item, "id", None),
                    "text": getattr(item, "text", ""),
                    "type": getattr(item, "type", None),
                    "metadata": getattr(item, "metadata", {}) or {},
                    "tags": getattr(item, "tags", []) or [],
                    "scores": getattr(item, "scores", None),
                })

            return results

        except Exception as e:
            logger.error(f"Hindsight recall error for bank '{bank_id}': {e}")
            return []
