from django.contrib import admin
from .models import *

@admin.register(AboutImage)
class AboutImageAdmin(admin.ModelAdmin):
    list_display = ("__str__",)




@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "updated_at")
    readonly_fields = ("updated_at",)
    filter_horizontal = ("images",)  # Makes ManyToMany selection easier




@admin.register(IconColor)
class IconColorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}  # auto-generate slug



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "popular", "updated_at","description")
    list_filter = ("category", "popular")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")




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



@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("title", "icon_class", "color", "order")
    search_fields = ("title", "description")
    list_editable = ("order",)
    ordering = ("order",)
