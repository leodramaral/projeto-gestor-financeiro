import smtplib

from django.core.management.base import BaseCommand, CommandError

from core.emailing import send_templated_email


class Command(BaseCommand):
    help = "Send a test email to validate the email configuration end to end."

    def add_arguments(self, parser):
        parser.add_argument("address", help="Recipient email address.")

    def handle(self, *args, **options):
        address = options["address"]
        try:
            send_templated_email(address, "E-mail de teste — Gestor Financeiro", "test_message")
        except (OSError, smtplib.SMTPException) as exc:
            # Only the exception type: the message could echo host or credentials.
            raise CommandError(
                f"Falha ao enviar o e-mail de teste ({type(exc).__name__})."
            ) from exc
        self.stdout.write(self.style.SUCCESS(f"E-mail de teste enviado para {address}."))
