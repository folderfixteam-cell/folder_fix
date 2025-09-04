from django.contrib import admin

from .models import *


# Register your models here.
@admin.register(NavLink)
class NavLinkAdmin(admin.ModelAdmin):
    list_display = ["title", "url", "order", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["title"]


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "page", "is_enabled", "order")
    list_filter = ("page", "is_enabled")
    search_fields = ("title", "subtitle", "cta_text")
    ordering = ("page", "order")

    fieldsets = (
        (
            "Placement",
            {
                "fields": ("page", "is_enabled", "order"),
            },
        ),
        (
            "Content",
            {
                "fields": ("title", "subtitle", "cta_text", "cta_url"),
            },
        ),
        (
            "Background",
            {
                "fields": (
                    "bg_gradient_from",
                    "bg_gradient_to",
                    "bg_image",
                    "bg_overlay_opacity",
                ),
                "description": "Use gradient only, or add an image (overlay applies when image is set).",
            },
        ),
    )




@admin.register(TitleSection)
class TitleSectionAdmin(admin.ModelAdmin):
    list_display = ("section_name", "heading", "subtitle", "is_enabled")
    list_filter = ("is_enabled",)
    search_fields = ("section_name", "heading", "subtitle")
    ordering = ("section_name",)



@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "mix_brand", "order")
    list_editable = ("order",)
    search_fields = ("name",)
    ordering = ("order",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    search_fields = ("name",)
    ordering = ("order",)


@admin.register(UniversalCombo)
class UniversalComboAdmin(admin.ModelAdmin):
    list_display = ("pk","main_model", "brand", "category", "active", "created_at")
    list_filter = ("brand", "category", "active")
    search_fields = ("main_model", "compatible_models", "description")
    prepopulated_fields = {"slug": ("main_model",)}
    ordering = ("brand", "category", "main_model")
    list_editable = ("active",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order")
    list_editable = ("order",)
    search_fields = ("question",)
    ordering = ("order",)


class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1
    fields = ("name", "url", "order")
    ordering = ("order",)


class FooterSectionInline(admin.StackedInline):
    model = FooterSection
    extra = 0
    fields = ("title", "order")
    ordering = ("order",)
    show_change_link = True


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1
    fields = ("platform", "icon_class", "url", "order")
    ordering = ("order",)


@admin.register(FooterSection)
class FooterSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "footer", "order")
    list_filter = ("footer",)
    ordering = ("footer", "order")
    inlines = [FooterLinkInline]


@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ("brand_name", "brand_highlight")
    inlines = [FooterSectionInline, SocialLinkInline]
    fieldsets = (
        ("Brand", {"fields": ("brand_icon", "brand_name", "brand_highlight")}),
        ("About", {"fields": ("about_text",)}),
        ("Legal", {"fields": ("copyright_text",)}),
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("footer", "enabled", "button_text")
    list_filter = ("enabled",)


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ("name", "section", "order")
    list_filter = ("section__footer", "section")
    ordering = ("section", "order")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("platform", "footer", "order")
    list_filter = ("footer",)
    ordering = ("footer", "order")


@admin.register(IconColor)
class IconColorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(WhyChooseItem)
class WhyChooseItemAdmin(admin.ModelAdmin):
    list_display = ("title", "icon_class", "color", "order", "is_enabled")
    list_editable = ("order", "is_enabled")
    list_filter = ("color", "is_enabled")
    search_fields = ("title", "description", "icon_class")
    ordering = ("order",)


@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ("title", "color", "order", "is_enabled", "updated_at")
    list_editable = ("order", "is_enabled")
    list_filter = ("color", "is_enabled")
    search_fields = ("title", "description", "icon_class", "icon_text")
    ordering = ("order",)
    fieldsets = (
        ("Content", {"fields": ("title", "description")}),
        (
            "Icon",
            {
                "fields": ("icon_text", "icon_class", "color"),
                "description": 'Use either <b>icon_text</b> (e.g. "U") or a Bootstrap icon class in <code>icon_class</code> (e.g. <code>bi-gem</code>).',
            },
        ),
        ("Placement & State", {"fields": ("order", "is_enabled")}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "badge_class")
    list_editable = ("badge_class",)
    search_fields = ("name", "badge_class")




@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "title", "role", "order", "is_enabled", "updated_at")
    list_editable = ("order", "is_enabled")
    list_filter = ("role", "is_enabled")
    search_fields = ("full_name", "title", "bio", "email_url")
    ordering = ("order", "id")
    fieldsets = (
        ("Identity", {"fields": ("full_name", "title", "role", "photo")}),
        ("Bio", {"fields": ("bio",)}),
        (
            "Socials & Contact",
            {
                "fields": ("whatsapp_url", "phone_url", "website_url", "email_url"),
                "description": "Leave blank to hide an icon.",
            },
        ),
        ("Placement & State", {"fields": ("order", "is_enabled")}),
    )


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("title", "icon_class", "color", "order")
    search_fields = ("title", "description")
    list_editable = ("order",)
    ordering = ("order",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "short_message", "created_at", "ip_address")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "message", "ip_address", "user_agent")
    readonly_fields = ("ip_address", "user_agent", "created_at")

    def short_message(self, obj):
        return (obj.message[:60] + "…") if len(obj.message) > 60 else obj.message

    short_message.short_description = "Message"





@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at",)




@admin.register(PolicySection)
class PolicySectionAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}



@admin.register(TermsSection)
class TermsSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order",)