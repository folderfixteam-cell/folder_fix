import json
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from app.models import UniversalCombo, Brand, Category

class Command(BaseCommand):
    help = "Import UniversalCombos from JSON safely"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Path to JSON file")

    def handle(self, *args, **kwargs):
        json_file = kwargs["json_file"]

        with open(json_file, "r") as f:
            data = json.load(f)

        objs = []
        existing_slugs = set(UniversalCombo.objects.values_list("slug", flat=True))

        for item in data:
            fields = item["fields"]

            # Ensure brand & category exist
            if not Brand.objects.filter(id=fields["brand"]).exists():
                self.stdout.write(self.style.WARNING(f"Skipping {fields['main_model']} → Brand {fields['brand']} not found"))
                continue
            if not Category.objects.filter(id=fields["category"]).exists():
                self.stdout.write(self.style.WARNING(f"Skipping {fields['main_model']} → Category {fields['category']} not found"))
                continue

            # Safe slug
            raw_slug = fields.get("slug") or slugify(f"{fields['main_model']}-{fields['brand']}-{fields['category']}")
            slug = raw_slug
            counter = 1
            while slug in existing_slugs:
                slug = f"{raw_slug}-{counter}"
                counter += 1
            existing_slugs.add(slug)

            objs.append(UniversalCombo(
                main_model=fields["main_model"],
                compatible_models=fields["compatible_models"],
                slug=slug,
                brand_id=fields["brand"],
                category_id=fields["category"],
                description=fields.get("description", ""),
                created_at=fields.get("created_at", timezone.now()),
                updated_at=fields.get("updated_at", timezone.now()),
                active=fields.get("active", True),
            ))

        UniversalCombo.objects.bulk_create(objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"✅ Inserted {len(objs)} UniversalCombos"))
