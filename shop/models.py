from django.db import models


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


class AboutImage(models.Model):
    image = models.ImageField(upload_to="about_images/")
    alt_text = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.alt_text or f"Image {self.id}"



class AboutSection(models.Model):
    description = models.TextField(blank=True, null=True)  # can include multiple paragraphs
    images = models.ManyToManyField(AboutImage, related_name="about_sections")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"About Section (Updated: {self.updated_at.strftime('%Y-%m-%d')})"


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/")
    popular = models.BooleanField(default=False)
    whatsapp_link = models.CharField(max_length=200,blank=True, null=True)
    call_link = models.CharField(max_length=20, blank=True, null=True)  # e.g., tel:+919999999999
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description=models.TextField(null=True,blank=True)
    is_available = models.BooleanField(default=False)




    class Meta:
        ordering = ["-popular", "-updated_at"]

    def __str__(self):
        return self.name


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



