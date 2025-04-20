# e_invoice_app/urls.py
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from e_invoice_app import settings

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ Prefix API versioning
    path("api/", include("invoices.urls")),

    # ✅ JWT Auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]+ static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
