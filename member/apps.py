from django.apps import AppConfig

class MemberConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "member"

    def ready(self):
        # Auto-create membership for new users
        from django.contrib.auth import get_user_model
        from django.db.models.signals import post_save
        from .models import Membership

        User = get_user_model()

        def ensure_membership(sender, instance, created, **kwargs):
            if created:
                Membership.objects.get_or_create(user=instance)
        post_save.connect(ensure_membership, sender=User)
