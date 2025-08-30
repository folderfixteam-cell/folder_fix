# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

class Membership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="membership")
    active = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_active(self):
        return self.active and (self.expires_at is None or self.expires_at > timezone.now())

    def extend_30_days(self, from_now=False):
        base = timezone.now() if from_now or not self.expires_at or self.expires_at < timezone.now() else self.expires_at
        self.expires_at = base + timedelta(days=30)
        self.active = True
        self.save(update_fields=["expires_at", "active", "updated_at"])

class Payment(models.Model):
    STATUS = [("created", "Created"), ("paid", "Paid"), ("failed", "Failed")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="member_payments")
    amount = models.IntegerField(help_text="Amount in paise")
    currency = models.CharField(max_length=10, default="INR")
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, blank=True)
    signature = models.CharField(max_length=256, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="created")
    receipt = models.CharField(max_length=64, default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user} ₹{self.amount/100:.2f} {self.status}"
