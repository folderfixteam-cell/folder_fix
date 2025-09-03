from django.db import models
from django.utils.text import slugify
from django.utils import timezone

# ========== Nav Link  Main ==========


class NavLink(models.Model):
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} - {self.url}"


class HeroSection(models.Model):
    PAGE_CHOICES = [
        ("home", "Home"),
        ("about", "About"),
        ("blog", "Blog"),
        ("shop", "Shop"),
        ("contact", "Contact"),
        ("faq", "FAQ"),
        ("privacy", "Privacy & Policy"),
        ("terms", "Terms & Conditions"),
        ("combo list","Combo List"),
        ("category list", "Category List"),
    ]

    page = models.CharField(max_length=32, choices=PAGE_CHOICES, default="home")
    is_enabled = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    title = models.CharField(max_length=160, default="Welcome to FolderFix")
    subtitle = models.CharField(
        max_length=240, default="Universal mobile solutions for all your needs."
    )

    cta_text = models.CharField(max_length=60, default="Explore Brands")
    cta_url = models.CharField(max_length=255, default="#brands")

    # ✅ Upload image instead of URL
    bg_image = models.ImageField(
        upload_to="hero/",  # stored in MEDIA_ROOT/hero/
        blank=True,
        null=True,
        help_text="Optional background image for hero section",
    )

    bg_gradient_from = models.CharField(max_length=20, default="#8e2de2")
    bg_gradient_to = models.CharField(max_length=20, default="#4a00e0")
    bg_overlay_opacity = models.FloatField(default=0.35)

    def __str__(self):
        return f"{self.page.title()} — {self.title[:30]}"

    @property
    def has_image(self):
        return bool(self.bg_image)


class IconColor(models.Model):
    """Simple reusable color model."""

    name = models.CharField(
        max_length=50, unique=True, help_text="E.g. green, blue, pink"
    )

    class Meta:
        verbose_name = "Icon Color"
        verbose_name_plural = "Icon Colors"
        ordering = ("name",)

    def __str__(self):
        return self.name



class TitleSection(models.Model):
    """Controls a section's heading/subtitle + enable/disable."""

    section_name = models.CharField(max_length=120, default="")
    heading = models.CharField(max_length=120, default="")
    subtitle = models.CharField(max_length=200, blank=True, default="")
    color_class = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Bootstrap color class (e.g. text-primary, text-success).",
    )
    icon_class = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Bootstrap icon class (e.g. bi bi-people).",
    )
    is_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Title — Section"
        verbose_name_plural = "Title  Sections"

    def __str__(self):
        return self.heading or "Untitled Section"



# ----------------------
# BRANDS
# ----------------------
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    mix_brand = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(unique=True, help_text="Used for URLs like /brand-vivo")
    color = models.ForeignKey(
        IconColor, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name}"


# ----------------------
# CATEGORIES
# ----------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(
        unique=True, help_text="Used for URLs like /category-battery"
    )
    color = models.ForeignKey(
        IconColor, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name}"


class UniversalCombo(models.Model):
    main_model = models.CharField(
        max_length=150,
        help_text="The main model name of the combo (e.g., Samsung Galaxy M12)",
    )
    compatible_models = models.TextField(
        help_text="List compatible models separated by commas or new lines"
    )
    slug = models.SlugField(unique=True, blank=True)

    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="universal_combos"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="universal_combos"
    )

    description = models.TextField(
        blank=True, help_text="Optional short description or notes"
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["brand", "category", "main_model"]
        verbose_name = "Universal Combo"
        verbose_name_plural = "Universal Combos"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f"{self.main_model}-{self.brand.name}-{self.category.name}"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.main_model} ({self.brand.name} - {self.category.name})"


# ========== Footer Main ==========
class Footer(models.Model):
    brand_name = models.CharField(max_length=100, default="FolderFix")
    brand_icon = models.CharField(max_length=10, default="📱")  # optional emoji/icon
    brand_highlight = models.CharField(max_length=50, default="Fix")
    about_text = models.TextField(
        default="Your trusted platform for mobile combo and folder matching — helping shops and technicians work faster, smarter, and better."
    )
    copyright_text = models.CharField(
        max_length=255, default="© 2025 FolderFix. All rights reserved."
    )

    def __str__(self):
        return f"Footer for {self.brand_name}"


# ----------------------
# FAQ
# ----------------------
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.question}"


# ========== Footer Link Sections ==========
class FooterSection(models.Model):
    footer = models.ForeignKey(
        Footer, related_name="sections", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)  # Example: Quick Links, Legal
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} Section"


class FooterLink(models.Model):
    section = models.ForeignKey(
        FooterSection, related_name="links", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)  # Example: Home, Contact
    url = models.CharField(max_length=255, default="")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} {self.section.title}"


# ========== Newsletter ==========
class Newsletter(models.Model):
    footer = models.OneToOneField(
        Footer, related_name="newsletter", on_delete=models.CASCADE
    )
    enabled = models.BooleanField(default=True)
    button_text = models.CharField(max_length=50, default="Subscribe")
    disclaimer = models.CharField(
        max_length=255, default="By subscribing, you agree to our Privacy Policy."
    )

    def __str__(self):
        return f"Newsletter ({'Enabled' if self.enabled else 'Disabled'})"


# ========== Social Links ==========
class SocialLink(models.Model):
    footer = models.ForeignKey(
        Footer, related_name="social_links", on_delete=models.CASCADE
    )
    platform = models.CharField(max_length=50)  # Example: Facebook, Instagram
    icon_class = models.CharField(
        max_length=50, help_text="Bootstrap Icon class, e.g., bi bi-facebook"
    )
    url = models.CharField(max_length=255, default="")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.platform} ({self.footer.brand_name})"


class WhyChooseItem(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    icon_class = models.CharField(
        max_length=40, default="bi-gem", help_text="Bootstrap Icon class, e.g. bi-gem"
    )
    color = models.ForeignKey(
        IconColor, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    order = models.PositiveSmallIntegerField(default=1)
    is_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Why Choose Item"
        verbose_name_plural = "Why Choose Items"

    def __str__(self):
        return f"{self.order:02d} — {self.title}"


class ServiceItem(models.Model):
    """Each card in the Services grid."""

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    # Put a letter, short label, or an icon class—whichever you prefer to render inside the circle.
    icon_text = models.CharField(
        max_length=12,
        blank=True,
        default="",
        help_text='Single letter like "U" or short text. Leave blank if using icon_class.',
    )
    icon_class = models.CharField(
        max_length=40,
        blank=True,
        default="",
        help_text="Bootstrap Icons class (e.g. bi-gem). Ignored if icon_text is provided.",
    )
    color = models.ForeignKey(
        IconColor, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    order = models.PositiveSmallIntegerField(default=1)
    is_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Service Item"
        verbose_name_plural = "Service Items"

    def __str__(self):
        return f"{self.order:02d} — {self.title}"

    @property
    def color_class(self):
        return self.color.name.lower() if self.color else "green"


class Role(models.Model):
    """Reusable team role with a badge CSS class name."""

    name = models.CharField(max_length=60, unique=True)  # e.g. Analyst, Designer
    badge_class = models.CharField(
        max_length=40,
        default="badge-analyst",
        help_text="CSS class to color the role badge (e.g. badge-analyst, badge-designer).",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """Each card in the team grid."""

    full_name = models.CharField(max_length=100)
    title = models.CharField(
        max_length=120, help_text="Job title shown under the name."
    )
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="members"
    )
    photo = models.ImageField(upload_to="team/", blank=True, null=True)
    bio = models.TextField(max_length=400, blank=True)
    order = models.PositiveSmallIntegerField(default=1)
    is_enabled = models.BooleanField(default=True)

    # quick socials (keep simple; add more if needed)
    phone_url = models.CharField(max_length=100,blank=True)
    whatsapp_url = models.CharField(max_length=100,blank=True)
    website_url = models.CharField(max_length=100,blank=True)
    email_url = models.CharField(max_length=100,blank=True)
    github_url = models.CharField(max_length=100,blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.order:02d} — {self.full_name}"


class ContactInfo(models.Model):
    ICON_CHOICES = [
        ("bi bi-geo-alt", "Address"),
        ("bi bi-telephone", "Phone"),
        ("bi bi-envelope", "Email"),
        ("bi bi-clock", "Timing"),
    ]

    title = models.CharField(
        max_length=100, help_text="Heading (e.g. Our Address, Call Us)"
    )
    description = models.TextField(
        help_text="Details like address, phone number, email etc."
    )
    icon_class = models.CharField(
        max_length=50,
        choices=ICON_CHOICES,
        default="bi bi-geo-alt",
        help_text="Bootstrap icon class",
    )
    color = models.ForeignKey(
        IconColor, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    order = models.PositiveIntegerField(default=0, help_text="Sorting order")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.title}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"



class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name}"



class PolicySection(models.Model):
    """
    A section in the Privacy Policy page (e.g. What we collect, How we use, etc.)
    """
    slug = models.SlugField(unique=True, help_text="Unique ID, e.g. 'what-we-collect'")
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class, e.g. 'bi bi-card-list'")
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text="Order of appearance")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title




class TermsSection(models.Model):
    """
    Each section of the Terms (Agreement, Accounts, Payments, etc.)
    """
    slug = models.SlugField(unique=True, help_text="Unique ID for section, e.g. 'agreement'")
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class, e.g. 'bi bi-patch-check-fill'")
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text="Order of appearance")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title
