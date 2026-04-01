import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_visitor_pass_email(visitor_pass):
    """
    Send approved visitor pass (QR + invite) to visitor's email.
    Returns (True, None) on success, (False, reason) on skip/failure.
    """
    email_addr = (visitor_pass.email or "").strip()
    if not email_addr:
        return False, "no_email"

    try:
        host_name = visitor_pass.host.get_full_name() or visitor_pass.host.username
        subject = f"Your visitor pass – GatePass QR (Pass #{visitor_pass.id})"
        context = {
            "pass": visitor_pass,
            "host_name": host_name,
        }
        html_body = render_to_string("emails/visitor_pass_approved.html", context)
        plain_body = (
            f"Hello {visitor_pass.visitor_name},\n\n"
            f"Your visit is approved.\n"
            f"Host: {host_name}\n"
            f"Valid from: {visitor_pass.valid_from}\n"
            f"Valid until: {visitor_pass.valid_until}\n"
            f"Purpose: {visitor_pass.purpose}\n\n"
            f"Your QR code is attached (visitor_pass_qr.png). Show it at the gate for entry.\n"
        )
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_addr],
        )
        msg.attach_alternative(html_body, "text/html")
        if visitor_pass.qr_image:
            with visitor_pass.qr_image.open("rb") as f:
                msg.attach("visitor_pass_qr.png", f.read(), "image/png")
        msg.send(fail_silently=False)
        return True, None
    except Exception as exc:
        logger.exception("Failed to send visitor pass email for pass_id=%s", visitor_pass.pk)
        return False, str(exc)
