"""Single entry point for sending transactional email rendered from templates."""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template, render_to_string


def send_templated_email(to, subject, template, context=None):
    """Send `templates/email/<template>.txt` and `.html` to `to` (an address or a list).

    The text part is always the body; the HTML part is attached as an alternative. `site_url`
    is added to the context so templates can build absolute links outside a request.
    """
    recipients = [to] if isinstance(to, str) else list(to)
    context = {**(context or {}), "site_url": settings.SITE_URL}

    # Plain text must keep characters like "&" literal, so it is rendered without autoescape.
    text_template = get_template(f"email/{template}.txt")
    text_body = text_template.template.render(Context(context, autoescape=False))
    html_body = render_to_string(f"email/{template}.html", context)

    message = EmailMultiAlternatives(subject=subject, body=text_body, to=recipients)
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)
    return message
