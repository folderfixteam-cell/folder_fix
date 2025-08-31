from django.urls import path

from .views import *

app_name = "app"

urlpatterns = [
path("", home_view, name="home"),
path("about/",about_view, name="about"),
path("contact/",contact_view, name="contact"),
path("combo-list/<slug:slug>",combo_list_view, name="combo-list"),
path("cate-list/<slug:slug>",cate_list_view, name="cate-list"),
path("privacy-policy/", privacy_policy, name="privacy-policy"),
path("terms-and-conditions/", terms_and_conditions, name="terms-and-conditions"),
path('faq/',faq_view,name="faq"),
path("robots.txt/", robots_txt, name="robots_txt"),
]
