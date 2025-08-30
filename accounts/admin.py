
from django.contrib import admin
from .models import Profile, EmailOTP

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_email_verified")
    search_fields = ("user__username", "user__email")

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "expires_at", "attempts_left", "created_at")
    list_filter = ("purpose", "expires_at", "created_at")
    search_fields = ("user__username", "user__email")


