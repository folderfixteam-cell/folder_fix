from .models import *
from django.conf import settings
from datetime import date


def common_context(page=" ", sec_name=""):
    # Navbar links (lean fields)
    nav_links = (
        NavLink.objects.filter(is_active=True)
        .only("title", "url", "order", "is_active")
        .order_by("order")
    )

    # Footer:
    # - newsletter is OneToOne -> select_related (1 query)
    # - sections->links + social_links -> prefetch_related (extra 1–2 queries total)
    footer = (
        Footer.objects.select_related("newsletter")
        .prefetch_related("sections__links", "social_links")
        .first()
    )

    # Hero section for the page
    hero = (
        HeroSection.objects.filter(is_enabled=True, page=page)
        .only(
            "page",
            "is_enabled",
            "order",
            "title",
            "subtitle",
            "cta_text",
            "cta_url",
            "bg_image",
            "bg_gradient_from",
            "bg_gradient_to",
            "bg_overlay_opacity",
        )
        .order_by("order")
        .first()
    )

    # Categories for nav/filters
    categories = Category.objects.only("name", "slug", "color", "order").order_by(
        "order"
    )

    return {
        "nav_links": nav_links,
        "footer": footer,
        "hero": hero,
        "categories": categories,
    }


def get_section_title(sec_name=" "):
    # Tiny table; fast lookup
    return TitleSection.objects.filter(is_enabled=True, section_name=sec_name).only(
        "section_name", "heading", "subtitle", "color_class", "icon_class", "is_enabled"
    ).first()


def get_home_context():
    ctx = common_context("home")
    ctx["brands"] = (
        Brand.objects.only("mix_brand", "slug", "color", "order").order_by("order")
    )
    ctx["combo_title"] = get_section_title("combo section")
    ctx["cate_title"] = get_section_title("category section")
    ctx["feedbacks"] = Feedback.objects.order_by("-created_at")[:10]
    return ctx


def get_about_context():
    ctx = common_context("about")
    ctx["choose_us"] = (
        WhyChooseItem.objects.filter(is_enabled=True)
        .only("title", "description", "icon_class", "color", "order", "is_enabled")
        .order_by("order")
    )
    ctx["services"] = (
        ServiceItem.objects.filter(is_enabled=True)
        .only("title", "description", "icon_text", "icon_class", "color", "order", "is_enabled")
        .order_by("order")
    )
    ctx["team_members"] = (
        TeamMember.objects.filter(is_enabled=True)
        .select_related("role")  # avoids N+1 if you show role.name
        .only(
            "full_name",
            "title",
            "role",
            "photo",
            "order",
            "is_enabled",
            "phone_url",
            "website_url",
            "whatsapp_url",
            "github_url",
            "email_url",
        )
        .order_by("order")
    )
    ctx["choose_title"] = get_section_title("choose section")
    ctx["service_title"] = get_section_title("service section")
    ctx["team_title"] = get_section_title("team section")
    return ctx


def get_contact_context():
    ctx = common_context("contact")
    ctx["contact_info"] = ContactInfo.objects.only(
        "title", "description", "icon_class", "color", "order"
    ).order_by("order")
    ctx["contact_title"] = get_section_title("contact section")
    ctx["map_title"] = get_section_title("map section")
    return ctx


def get_faq_context():
    ctx = common_context("faq")
    ctx["faqs"] = (
        FAQ.objects.only("question", "answer", "order")
        .order_by("-pk")[:20]
    )
    ctx["faq_title"] = get_section_title("faq section")
    return ctx


def get_privacy_context():
    ctx = common_context("privacy")
    privacy_sections = PolicySection.objects.all()
    ctx.update(
        {
            "privacy_last_updated": date(2025, 8, 28),
            "privacy_sections": privacy_sections ,
            "site_name": getattr(settings, "SITE_NAME", "FolderFix"),
            "support_email": getattr(settings, "DEFAULT_FROM_EMAIL", "support@example.com"),
        }
    )
    return ctx


def get_term_context():
    ctx = common_context("terms")
    term_sections = TermsSection.objects.all()
    ctx.update(
        {
            "terms_last_updated": date(2025, 8, 28),
            "term_sections":term_sections,
            "site_name": getattr(settings, "SITE_NAME", "FolderFix"),
        }
    )
    return ctx


def get_combo_list(slug):
    ctx = common_context("combo list")
    # Join brand/category to prevent N+1 in templates
    ctx["combo_list"] = (
        UniversalCombo.objects.select_related("brand", "category")
        .filter(brand__slug__iexact=slug.lower())
        .only(
            "main_model",
            "compatible_models",
            "slug",
            "description",
            "active",
            "created_at",
            "updated_at",
            "brand__name",
            "brand__slug",
            "category__name",
            "category__slug",
        )
    )
    ctx["slug"] = slug
    return ctx


def get_category_list(slug):
    ctx = common_context("home")
    ctx["cate_list"] = (
        UniversalCombo.objects.select_related("brand", "category")
        .filter(category__slug__iexact=slug.lower())
        .only(
            "main_model",
            "compatible_models",
            "slug",
            "description",
            "active",
            "created_at",
            "updated_at",
            "brand__name",
            "brand__slug",
            "category__name",
            "category__slug",
        )
    )
    ctx["slug"] = slug
    return ctx
