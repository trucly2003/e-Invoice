from django.urls import path, include
from rest_framework.routers import DefaultRouter
from invoices.views import ExtractedInvoiceViewSet, UploadInvoiceViewSet  # ✅ Nhớ chắc chắn rằng ViewSet này được import đúng
from .auth_api import login_view

router = DefaultRouter()
router.register("invoices", ExtractedInvoiceViewSet, basename="invoice")
router.register(r'upload-invoice', UploadInvoiceViewSet, basename='upload-invoice')

urlpatterns = [
    path("", include(router.urls)),
    path("login/", login_view, name="login"),
]