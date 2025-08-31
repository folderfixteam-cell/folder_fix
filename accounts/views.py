import logging
from typing import Any, Dict
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import (
    SignUpForm,
    LoginForm,
    OTPForm,
    PasswordResetEmailForm,
    SetPasswordForm,
    UserUpdateForm,
)
from .models import Profile
from .utils import create_or_refresh_otp, send_otp_email, verify_otp
from app.utils import common_context
from member.models import Membership

logger = logging.getLogger(__name__)

PRICE_RUPEES = 25
PRICE_PAISE = PRICE_RUPEES * 100


def _client_ip(req: HttpRequest) -> str:
    """Get the real client IP (works behind PythonAnywhere/Nginx proxy)."""
    xff = req.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return req.META.get("REMOTE_ADDR", "")


def _safe_redirect(default: str, named: str, **kwargs) -> HttpResponse:
    """Helper for safe reverse() with fallback"""
    try:
        return redirect(reverse(named, kwargs=kwargs))
    except Exception:
        return redirect(default)


# ---------- Dashboard ----------

@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    try:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        m, _ = Membership.objects.get_or_create(user=request.user)
    except Exception as e:
        logger.exception("dashboard_view error: %s", e)
        messages.error(request, "⚠️ Unable to load dashboard.")
        return redirect("/")

    ip = _client_ip(request)
    logger.info("Dashboard viewed by user %s from IP %s", request.user.username, ip)

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(request, "✅ Profile updated successfully.")
                return _safe_redirect("/dashboard", "accounts:dashboard")
            except Exception as e:
                logger.exception("dashboard_view save error: %s", e)
                messages.error(request, "⚠️ Could not update profile. Try again.")
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = UserUpdateForm(instance=request.user)

    ctx: Dict[str, Any] = common_context()
    ctx.update(
        {
            "profile": profile,
            "user_obj": request.user,
            "form": form,
            "membership": m,
            "is_active": m.is_active(),
            "price_rupees": PRICE_RUPEES,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        }
    )
    return render(request, "accounts/dashboard.html", ctx)


# ---------- Sign Up & Verify Email ----------

@require_http_methods(["GET", "POST"])
def signup_view(request: HttpRequest) -> HttpResponse:
    ctx: Dict[str, Any] = common_context()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.username = form.cleaned_data["username"]
                    user.email = form.cleaned_data["email"].lower()
                    user.set_password(form.cleaned_data["password1"])
                    user.save()

                    Profile.objects.get_or_create(user=user)

                    ip = _client_ip(request)
                    logger.info("New signup: %s from IP %s", user.username, ip)

                    otp, rec_or_err = create_or_refresh_otp(user, "verify_email")
                    if not otp:
                        messages.error(request, rec_or_err)
                        return _safe_redirect("/signup", "accounts:verify-email", user_id=user.id)

                    send_otp_email(user, "verify_email", otp)
                    messages.success(request, "✅ We sent an OTP to your email. Please verify.")
                    return _safe_redirect("/signup", "accounts:verify-email", user_id=user.id)
            except Exception as e:
                logger.exception("signup_view error: %s", e)
                messages.error(request, "⚠️ Could not complete signup. Please try again.")
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
        ctx["form"] = form
        return render(request, "accounts/signup.html", ctx)

    ctx["form"] = SignUpForm()
    return render(request, "accounts/signup.html", ctx)


@require_http_methods(["GET", "POST"])
def verify_email_view(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, id=user_id)
    form = OTPForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            ok, msg = verify_otp(user, "verify_email", form.cleaned_data["otp"])
            if ok:
                Profile.objects.filter(user=user).update(is_email_verified=True)
                ip = _client_ip(request)
                logger.info("Email verified for %s from IP %s", user.username, ip)

                messages.success(request, "✅ Email verified. You can log in now.")
                return _safe_redirect("/login", "accounts:login")
            messages.error(request, msg)
        except Exception as e:
            logger.exception("verify_email_view error: %s", e)
            messages.error(request, "⚠️ Could not verify email. Please try again.")

    ctx: Dict[str, Any] = common_context()
    ctx.update({"form": form, "user": user})
    return render(request, "accounts/verify_email.html", ctx)


@require_http_methods(["POST"])
def resend_verification_otp(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, id=user_id)
    try:
        otp, rec_or_err = create_or_refresh_otp(user, "verify_email")
        if not otp:
            messages.error(request, rec_or_err)
        else:
            ip = _client_ip(request)
            logger.info("Resent verification OTP for %s from IP %s", user.username, ip)

            send_otp_email(user, "verify_email", otp)
            messages.success(request, "✅ OTP resent to your email.")
    except Exception as e:
        logger.exception("resend_verification_otp error: %s", e)
        messages.error(request, "⚠️ Could not resend OTP.")
    return _safe_redirect("/signup", "accounts:verify-email", user_id=user.id)


# ---------- Login / Logout ----------

@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    ctx: Dict[str, Any] = common_context()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = form.cleaned_data["user"]
                profile, _ = Profile.objects.get_or_create(user=user)

                ip = _client_ip(request)
                logger.info("User %s attempting login from IP %s", user.username, ip)

                if not profile.is_email_verified:
                    otp, rec_or_err = create_or_refresh_otp(user, "verify_email")
                    if otp:
                        send_otp_email(user, "verify_email", otp)
                    messages.warning(request, "⚠️ Please verify your email before logging in.")
                    return _safe_redirect("/login", "accounts:verify-email", user_id=user.id)

                login(request, user)
                messages.success(request, "✅ Welcome back!")
                return redirect("/")
            except Exception as e:
                logger.exception("login_view error: %s", e)
                messages.error(request, "⚠️ Login failed. Please try again.")
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
        ctx["form"] = form
        return render(request, "accounts/login.html", ctx)

    ctx["form"] = LoginForm()
    return render(request, "accounts/login.html", ctx)


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    try:
        ip = _client_ip(request)
        logger.info("User %s logged out from IP %s", request.user.username, ip)

        logout(request)
        messages.info(request, "ℹ️ You are logged out.")
    except Exception as e:
        logger.exception("logout_view error: %s", e)
        messages.error(request, "⚠️ Logout failed.")
    return _safe_redirect("/login", "accounts:login")


# ---------- Password Reset (OTP flow) ----------

@require_http_methods(["GET", "POST"])
def password_reset_request_view(request: HttpRequest) -> HttpResponse:
    ctx: Dict[str, Any] = common_context()
    form = PasswordResetEmailForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            email = form.cleaned_data["email"].lower()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.success(request, "✅ If the email exists, you will receive an OTP.")
                return _safe_redirect("/reset", "accounts:password-reset-request")

            otp, rec_or_err = create_or_refresh_otp(user, "password_reset")
            if not otp:
                messages.error(request, rec_or_err)
                return _safe_redirect("/reset", "accounts:password-reset-request")

            ip = _client_ip(request)
            logger.info("Password reset OTP requested for %s from IP %s", user.username, ip)

            send_otp_email(user, "password_reset", otp)
            messages.success(request, "✅ OTP sent for password reset.")
            return _safe_redirect("/reset", "accounts:password-reset-verify", user_id=user.id)
        except Exception as e:
            logger.exception("password_reset_request_view error: %s", e)
            messages.error(request, "⚠️ Could not send password reset OTP.")
    ctx["form"] = form
    return render(request, "accounts/password_reset_request.html", ctx)


@require_http_methods(["GET", "POST"])
def password_reset_verify_view(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, id=user_id)
    form = OTPForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            ok, msg = verify_otp(user, "password_reset", form.cleaned_data["otp"])
            if ok:
                ip = _client_ip(request)
                logger.info("Password reset OTP verified for %s from IP %s", user.username, ip)

                request.session["pw_reset_user_id"] = user.id
                return _safe_redirect("/reset", "accounts:password-reset-set")
            messages.error(request, msg)
        except Exception as e:
            logger.exception("password_reset_verify_view error: %s", e)
            messages.error(request, "⚠️ Could not verify OTP.")
    ctx: Dict[str, Any] = common_context()
    ctx.update({"form": form, "user": user})
    return render(request, "accounts/password_reset_verify.html", ctx)


@require_http_methods(["GET", "POST"])
def password_reset_set_view(request: HttpRequest) -> HttpResponse:
    user_id = request.session.get("pw_reset_user_id")
    if not user_id:
        messages.error(request, "⚠️ Session expired. Start again.")
        return _safe_redirect("/reset", "accounts:password-reset-request")

    user = get_object_or_404(User, id=user_id)
    form = SetPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user.set_password(form.cleaned_data["new_password1"])
                user.save()
                request.session.pop("pw_reset_user_id", None)

            ip = _client_ip(request)
            logger.info("Password reset completed for %s from IP %s", user.username, ip)

            messages.success(request, "✅ Password updated. Please log in.")
            return _safe_redirect("/login", "accounts:login")
        except Exception as e:
            logger.exception("password_reset_set_view error: %s", e)
            messages.error(request, "⚠️ Could not reset password.")
    ctx: Dict[str, Any] = common_context()
    ctx["form"] = form
    return render(request, "accounts/password_reset_set.html", ctx)
