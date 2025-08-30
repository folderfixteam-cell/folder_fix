# app/views.py
from __future__ import annotations

import logging
from typing import Dict, Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, NoReverseMatch
from django.views.decorators.http import require_http_methods

from .forms import ContactForm, FAQForm,FeedbackForm
from .utils import (
    get_home_context,
    get_about_context,
    get_contact_context,
    get_faq_context,
    get_privacy_context,
    get_term_context,
    get_combo_list,
    get_category_list,
)
from member.decorators import membership_required  # keep if you plan to enforce

logger = logging.getLogger(__name__)


# --------- helpers ---------
def _safe_reverse(fallback_path: str, name: str) -> str:
    """
    Reverse a named URL; fall back to a path string if the name isn't registered.
    Helps avoid runtime errors if URL names differ across envs.
    """
    try:
        return reverse(name)
    except NoReverseMatch:
        return fallback_path


def _client_ip(req: HttpRequest) -> str:
    # Respect reverse proxies (Nginx) if X-Forwarded-For is configured
    xff = req.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return req.META.get("REMOTE_ADDR", "")


# --------- pages ---------
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
def home_view(request: HttpRequest) -> HttpResponse:
    try:
        ctx = get_home_context()
    except Exception as e:
        logger.exception("home_view context error: %s", e)
        ctx = {}

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(
                    request, "✅ Thanks for your feedback! We truly appreciate it."
                )
                ctx["form"] = FeedbackForm()
                return render(request, "app/index.html", ctx)  # change to your actual home URL name
            except Exception as e:
                logger.exception("home_view feedback save error: %s", e)
                messages.error(
                    request, "⚠️ Could not submit your feedback. Please try again."
                )
        else:
            messages.error(request, "⚠️ Please fix the errors below.")
        ctx["form"] = form
        return render(request, "app/index.html", ctx)

    # GET
    ctx["form"] = FeedbackForm()
    return render(request, "app/index.html", ctx)










@require_http_methods(["GET"])
def about_view(request: HttpRequest) -> HttpResponse:
    try:
        ctx = get_about_context()
    except Exception as e:
        logger.exception("about_view context error: %s", e)
        ctx = {}
    return render(request, "app/about.html", ctx)


@require_http_methods(["GET", "POST"])
def contact_view(request: HttpRequest) -> HttpResponse:
    try:
        ctx: Dict[str, Any] = get_contact_context()
    except Exception as e:
        logger.exception("contact_view context error: %s", e)
        ctx = {}

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    obj = form.save(commit=False)
                    obj.ip_address = _client_ip(request)[:45]  # IPv6-safe
                    obj.user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:500]
                    obj.save()
                messages.success(
                    request,
                    "✅ Your message has been sent. We’ll get back to you soon!",
                )
                return redirect(_safe_reverse("/contact", "app:contact"))
            except Exception as e:
                logger.exception("contact_view save error: %s", e)
                messages.error(
                    request,
                    "⚠️ We couldn’t submit your message right now. Please try again.",
                )
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
        # on POST fall-through, re-render with bound form
        ctx["form"] = form
        return render(request, "app/contact.html", ctx)

    # GET
    ctx["form"] = ContactForm()
    return render(request, "app/contact.html", ctx)


@login_required(login_url="accounts:login")
# @membership_required  # uncomment when membership gating is ready
@require_http_methods(["GET"])
def combo_list_view(request: HttpRequest, slug: str) -> HttpResponse:
    try:
        ctx = get_combo_list(slug)
    except Exception as e:
        logger.exception("combo_list_view context error for slug=%s: %s", slug, e)
        messages.error(request, "⚠️ Unable to load combos right now.")
        ctx = {"slug": slug, "items": []}
    return render(request, "app/combo-list.html", ctx)


@login_required(login_url="accounts:login")
# @membership_required  # uncomment when membership gating is ready
@require_http_methods(["GET"])
def cate_list_view(request: HttpRequest, slug: str) -> HttpResponse:
    try:
        ctx = get_category_list(slug)
    except Exception as e:
        logger.exception("cate_list_view context error for slug=%s: %s", slug, e)
        messages.error(request, "⚠️ Unable to load categories right now.")
        ctx = {"slug": slug, "items": []}
    return render(request, "app/cate-list.html", ctx)


@require_http_methods(["GET"])
def privacy_policy(request: HttpRequest) -> HttpResponse:
    try:
        ctx = get_privacy_context()
    except Exception as e:
        logger.exception("privacy_policy context error: %s", e)
        ctx = {}
    return render(request, "app/privacy_policy.html", ctx)


@require_http_methods(["GET"])
def terms_and_conditions(request: HttpRequest) -> HttpResponse:
    try:
        ctx = get_term_context()
    except Exception as e:
        logger.exception("terms_and_conditions context error: %s", e)
        ctx = {}
    return render(request, "app/terms_and_conditions.html", ctx)


@require_http_methods(["GET", "POST"])
def faq_view(request: HttpRequest) -> HttpResponse:
    try:
        ctx: Dict[str, Any] = get_faq_context()
    except Exception as e:
        logger.exception("faq_view context error: %s", e)
        ctx = {}

    if request.method == "POST":
        form = FAQForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(
                    request, "✅ Thanks! We’ll answer your question as soon as possible."
                )
                return redirect(_safe_reverse("/faq", "app:faq"))
            except Exception as e:
                logger.exception("faq_view save error: %s", e)
                messages.error(
                    request, "⚠️ Could not submit your question. Please try again."
                )
        else:
            messages.error(request, "⚠️ Please fix the errors below.")
        ctx["form"] = form
        return render(request, "app/faq.html", ctx)

    # GET
    ctx["form"] = FAQForm()
    return render(request, "app/faq.html", ctx)







def Handler404View(request, exeption):
    return render(request, "errors/404.html", status=404)

