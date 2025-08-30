
from django.contrib import admin
from .models import Membership, Payment

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "active", "expires_at", "updated_at")
    list_filter = ("active",)
    search_fields = ("user__username", "user__email")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "order_id", "status", "amount", "created_at")
    list_filter = ("status",)
    search_fields = ("order_id", "payment_id", "user__username", "user__email")
