from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from app.models import UniversalCombo, Category  # अपने models के सही नाम से import करें


# --- Static pages sitemap ---
class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return [
            'app:home',
            'app:about',
            'app:contact',
            'app:privacy-policy',
            'app:terms-and-conditions',
            'app:faq',
        ]

    def location(self, item):
        return reverse(item)


# --- Combo pages sitemap ---
class ComboSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return UniversalCombo.objects.all()

    def location(self, obj):
        return reverse("app:combo-list", kwargs={"slug": obj.slug})


# --- Category pages sitemap ---
class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse("app:cate-list", kwargs={"slug": obj.slug})
