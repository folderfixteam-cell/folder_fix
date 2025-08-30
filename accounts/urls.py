# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("verify/<int:user_id>/", views.verify_email_view, name="verify-email"),
    path("verify/<int:user_id>/resend/", views.resend_verification_otp, name="resend-otp"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),

    path("password-reset/", views.password_reset_request_view, name="password-reset-request"),
    path("password-reset/<int:user_id>/verify/", views.password_reset_verify_view, name="password-reset-verify"),
    path("password-reset/set/", views.password_reset_set_view, name="password-reset-set"),
]
