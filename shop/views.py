from django.shortcuts import render
from .models import *
from django.db.models import Max
from app.utils import common_context
# Create your views here.
import re
import logging
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods


logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
@cache_page(60 * 5) 
def shop_view(request):
    try:
        ctx=common_context("shop")
        about = AboutSection.objects.last()
        products = Product.objects.select_related("category").all()
        categories = Category.objects.all()
        max_price = products.aggregate(Max('price'))['price__max'] or 500  # fallback
        services= (
            ServiceItem.objects.filter(is_enabled=True)
            .only("title", "description", "icon_text", "icon_class", "color", "order", "is_enabled")
            .order_by("order")
        )
        contact_info= ContactInfo.objects.only(
            "title", "description", "icon_class", "color", "order"
        ).order_by("order")
    
        ctx.update( {
            "about": about,
            "products": products,
            "categories": categories,
            "max_price": max_price,
            "services":services,
            "contact_info":contact_info
        })
    except Exception as e:
        logger.exception("Error loading shop page context")
        ctx = {
            "about": None,
            "products": [],
            "categories": [],
            "max_price": 500,
            "services": [],
            "contact_info": [],
        }
   
    return render(request, "shop/shop.html", ctx)



