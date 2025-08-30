# accounts/utils.py
import os
import hmac
import secrets
import hashlib
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from .models import EmailOTP

def _make_otp(length=6) -> str:
    # Numeric OTP (no leading zeros loss when treated as string)
    return "".join(secrets.choice("0123456789") for _ in range(length))

def _hash_otp(otp: str, salt: str) -> str:
    # HMAC with SECRET_KEY -> sha256
    return hmac.new(key=settings.SECRET_KEY.encode(), msg=(salt + otp).encode(), digestmod=hashlib.sha256).hexdigest()

def create_or_refresh_otp(user, purpose: str):
    # Throttle resends
    otp_qs = EmailOTP.objects.filter(user=user, purpose=purpose).order_by("-created_at")
    latest = otp_qs.first()
    now = timezone.now()
    if latest and latest.last_sent_at and (now - latest.last_sent_at).total_seconds() < settings.OTP_RESEND_INTERVAL_SECONDS:
        return None, "Please wait before requesting another OTP."

    otp = _make_otp(settings.OTP_LENGTH)
    salt = secrets.token_hex(8)
    otp_hash = _hash_otp(otp, salt)
    expires_at = now + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    record = EmailOTP.objects.create(
        user=user,
        purpose=purpose,
        otp_hash=otp_hash,
        otp_salt=salt,
        expires_at=expires_at,
        attempts_left=getattr(settings, "OTP_MAX_ATTEMPTS", 5),
        last_sent_at=now,
    )
    return otp, record

def verify_otp(user, purpose: str, otp_input: str):
    rec = (
        EmailOTP.objects.filter(user=user, purpose=purpose)
        .order_by("-created_at")
        .first()
    )
    if not rec:
        return False, "No OTP found. Please request a new one."
    if rec.is_expired():
        return False, "OTP has expired. Request a new one."
    if rec.attempts_left == 0:
        return False, "Too many wrong attempts. Request a new OTP."

    expected = _hash_otp(otp_input, rec.otp_salt)
    if not hmac.compare_digest(expected, rec.otp_hash):
        rec.attempts_left = max(0, rec.attempts_left - 1)
        rec.save(update_fields=["attempts_left"])
        left = rec.attempts_left
        return False, f"Incorrect OTP. Attempts left: {left}"
    return True, "OK"

def send_otp_email(user, purpose: str, otp: str):
    subject = f"{settings.SITE_NAME} - Your OTP"
    context = {
        "site_name": settings.SITE_NAME,
        "site_domain": settings.SITE_DOMAIN,
        "user": user,
        "otp": otp,
        "purpose": purpose,
        "minutes": settings.OTP_EXPIRY_MINUTES,
    }
    text_body = render_to_string("accounts/emails/otp_email.txt", context)
    html_body = render_to_string("accounts/emails/otp_email.html", context)
    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)
