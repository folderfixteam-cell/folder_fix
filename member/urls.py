from django.urls import path
from . import views

app_name = "member"

urlpatterns = [
    path("create-order/", views.create_order, name="create-order"),
    path("verify/", views.verify_checkout_signature, name="verify"),
]
