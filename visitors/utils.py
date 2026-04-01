from io import BytesIO
import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.signing import BadSignature, TimestampSigner
from django.utils import timezone


def get_signer():
    return TimestampSigner(salt=settings.QR_SIGNING_SALT)


def create_qr_token(visitor_pass):
    payload = f"{visitor_pass.id}|{visitor_pass.host_id}|{visitor_pass.valid_from.isoformat()}|{visitor_pass.valid_until.isoformat()}"
    return get_signer().sign(payload)


def validate_qr_token(token):
    try:
        data = get_signer().unsign(token, max_age=60 * 60 * 24 * 7)
        pass_id = int(data.split("|")[0])
        return pass_id, None
    except (BadSignature, ValueError):
        return None, "Invalid signature"


def generate_qr_image(visitor_pass):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(visitor_pass.qr_token)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    file_name = f"pass_{visitor_pass.id}.png"
    visitor_pass.qr_image.save(file_name, ContentFile(buffer.getvalue()), save=False)


def refresh_expired_passes():
    from .models import VisitorPass

    now = timezone.now()
    VisitorPass.objects.filter(valid_until__lt=now, status__in=["approved", "checked_in"]).update(status="expired")
