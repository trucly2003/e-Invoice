from django.urls import path, include
from rest_framework.routers import DefaultRouter
from invoices.views import ExtractedInvoiceViewSet, UploadInvoiceViewSet  # ✅ Nhớ chắc chắn rằng ViewSet này được import đúng

router = DefaultRouter()
router.register("invoices", ExtractedInvoiceViewSet, basename="invoice")
router.register(r'upload-invoice', UploadInvoiceViewSet, basename='upload-invoice')

urlpatterns = [
    path("", include(router.urls)),
]