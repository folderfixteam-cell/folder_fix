"""
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from django.contrib.sitemaps.views import sitemap
from .sitemap import StaticViewSitemap, ComboSitemap, CategorySitemap

sitemaps = {
    "static": StaticViewSitemap,
    "combo": ComboSitemap,
    "category": CategorySitemap,
}




urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("app.urls","app"),namespace="app")),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("member/", include(("member.urls","member"),namespace="member")),
    path("shop/", include(("shop.urls","shop"), namespace="shop")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),

]

handler404 = "app.views.Handler404View"




