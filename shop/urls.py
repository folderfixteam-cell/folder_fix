from django.urls import path
from .views import *

app_name="shop"

urlpatterns = [
    path("", shop_view, name="shop"),
    # path("details/<int:pk>", details_view, name="details"),
]
