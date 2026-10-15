"""The one place the provider client is created, so tests can swap it."""

from django.conf import settings
from openai import OpenAI


def get_client():
    """A client for the configured OpenAI-compatible provider.

    No automatic retries: a hidden retry would spend quota without the user knowing.
    """
    return OpenAI(
        base_url=settings.LLM_BASE_URL,
        api_key=settings.LLM_API_KEY,
        timeout=settings.LLM_TIMEOUT_SECONDS,
        max_retries=0,
    )
