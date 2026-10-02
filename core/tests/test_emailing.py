import smtplib
from unittest import mock

import pytest
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.core.management.base import CommandError

from core.emailing import send_templated_email


def test_test_settings_use_locmem_backend():
    assert settings.EMAIL_BACKEND.endswith("locmem.EmailBackend")


def test_sends_text_and_html_in_portuguese():
    send_templated_email("a@example.com", "Assunto", "test_message")

    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert message.to == ["a@example.com"]
    assert message.subject == "Assunto"
    assert "e-mail de teste do Gestor Financeiro" in message.body
    html, mimetype = message.alternatives[0]
    assert mimetype == "text/html"
    assert 'lang="pt-br"' in html
    assert "e-mail de teste do Gestor Financeiro" in html


def test_link_starts_with_site_url():
    send_templated_email("a@example.com", "Assunto", "test_message")

    message = mail.outbox[0]
    assert f"{settings.SITE_URL}/" in message.body
    assert f'href="{settings.SITE_URL}/"' in message.alternatives[0][0]


def test_context_is_escaped_in_html_and_literal_in_text(tmp_path, settings):
    templates = tmp_path / "email"
    templates.mkdir()
    (templates / "echo.txt").write_text("{{ value }}")
    (templates / "echo.html").write_text("<p>{{ value }}</p>")
    settings.TEMPLATES = [
        {**settings.TEMPLATES[0], "DIRS": [tmp_path, *settings.TEMPLATES[0]["DIRS"]]}
    ]

    send_templated_email("a@example.com", "Assunto", "echo", {"value": "<script>x</script> & y"})

    message = mail.outbox[0]
    assert message.body == "<script>x</script> & y"
    html = message.alternatives[0][0]
    assert "&lt;script&gt;x&lt;/script&gt; &amp; y" in html
    assert "<script>" not in html


def test_subject_with_newline_is_rejected():
    with pytest.raises(ValueError):
        send_templated_email("a@example.com", "Oi\nBcc: x@example.com", "test_message")
    assert mail.outbox == []


def test_command_sends_test_email():
    call_command("send_test_email", "dev@example.com")

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["dev@example.com"]


@pytest.mark.parametrize(
    "error", [smtplib.SMTPException("secret-host"), ConnectionRefusedError("secret-host")]
)
def test_command_reports_connection_failure_without_config(error):
    with mock.patch("core.emailing.EmailMultiAlternatives.send", side_effect=error):
        with pytest.raises(CommandError) as exc_info:
            call_command("send_test_email", "dev@example.com")

    assert "Falha ao enviar" in str(exc_info.value)
    assert "secret-host" not in str(exc_info.value)
