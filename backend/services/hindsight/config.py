"""
Hindsight Configuration for Gram Vaani
Handles loading and safe validation of Hindsight memory parameters from environment variables.
"""

import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class HindsightConfig:
    api_key: Optional[str]
    base_url: str
    bank_id: str
    timeout_seconds: float = 30.0
    max_retries: int = 3

    @property
    def is_configured(self) -> bool:
        """Returns True only if minimal required configuration is present."""
        return bool(self.api_key and self.api_key.strip() and self.base_url and self.base_url.strip())

    @property
    def masked_api_key(self) -> str:
        """Returns masked API key for safe logging without exposing secrets."""
        if not self.api_key:
            return "<not set>"
        clean = self.api_key.strip()
        if len(clean) <= 8:
            return "***"
        return f"{clean[:4]}...{clean[-4:]}"

    def __repr__(self) -> str:
        return (
            f"HindsightConfig(base_url='{self.base_url}', "
            f"bank_id='{self.bank_id}', "
            f"api_key='{self.masked_api_key}', "
            f"is_configured={self.is_configured})"
        )


def get_hindsight_config() -> HindsightConfig:
    """
    Load Hindsight configuration from environment variables.
    Never raises an exception; gracefully detects missing configuration.
    """
    api_key = os.getenv("HINDSIGHT_API_KEY")
    base_url = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io").strip()
    bank_id = os.getenv("HINDSIGHT_BANK_ID", "sarthi").strip()
    
    timeout_raw = os.getenv("HINDSIGHT_TIMEOUT", "30.0")
    try:
        timeout = float(timeout_raw)
    except ValueError:
        timeout = 30.0

    return HindsightConfig(
        api_key=api_key.strip() if api_key else None,
        base_url=base_url if base_url else "https://api.hindsight.vectorize.io",
        bank_id=bank_id if bank_id else "sarthi",
        timeout_seconds=timeout,
    )
