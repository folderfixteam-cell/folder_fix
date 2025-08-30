from django.db import models
# Create your models here.
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile<{self.user.username}>"

class EmailOTP(models.Model):
    PURPOSE_CHOICES = [
        ("verify_email", "Verify Email"),
        ("password_reset", "Password Reset"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICES)
    otp_hash = models.CharField(max_length=128)
    otp_salt = models.CharField(max_length=32)
    expires_at = models.DateTimeField()
    attempts_left = models.PositiveIntegerField(default=5)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "purpose", "-created_at"]),
        ]

    def is_expired(self):
        return timezone.now() >= self.expires_at


