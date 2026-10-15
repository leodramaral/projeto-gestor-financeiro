import pytest

from assistant.client import get_client


def test_creating_the_real_client_fails_the_test():
    with pytest.raises(AssertionError, match="real LLM client"):
        get_client()
