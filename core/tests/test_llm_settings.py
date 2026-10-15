import json
import os
import subprocess
import sys

BASE_ENV = {"SECRET_KEY": "x", "DATABASE_URL": "postgres://u:p@localhost/db"}


def read_settings(extra=None):
    """The LLM settings as a fresh process sees them, with only the given variables set."""
    env = {"PATH": os.environ["PATH"], **BASE_ENV, **(extra or {})}
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json, config.settings.base as s;"
            "print(json.dumps([s.LLM_API_KEY, s.LLM_BASE_URL, s.LLM_MODEL, "
            "s.LLM_DAILY_TOKEN_LIMIT, s.LLM_TIMEOUT_SECONDS]))",
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_app_starts_without_the_provider_key():
    key, *_ = read_settings()

    assert key == ""


def test_defaults_point_to_groq_and_cap_the_daily_tokens():
    _, base_url, model, daily_limit, timeout = read_settings()

    assert base_url == "https://api.groq.com/openai/v1"
    assert model == "openai/gpt-oss-120b"
    assert daily_limit == 40000
    assert timeout == 20


def test_environment_overrides_the_defaults():
    key, base_url, model, daily_limit, timeout = read_settings(
        {
            "LLM_API_KEY": "k",
            "LLM_BASE_URL": "https://example.com/v1",
            "LLM_MODEL": "other-model",
            "LLM_DAILY_TOKEN_LIMIT": "1000",
            "LLM_TIMEOUT_SECONDS": "5",
        }
    )

    assert (key, base_url, model, daily_limit, timeout) == (
        "k",
        "https://example.com/v1",
        "other-model",
        1000,
        5,
    )
