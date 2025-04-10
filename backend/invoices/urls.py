from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExtractedInvoiceViewSet, UploadInvoiceViewSet, SignatureVerificationViewSet
from .auth_api import login_view


router = DefaultRouter()
router.register("invoices", ExtractedInvoiceViewSet, basename="invoice")
router.register(r'upload-invoice', UploadInvoiceViewSet, basename='upload-invoice')
router.register("signature-verification", SignatureVerificationViewSet, basename="signature-verification")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", login_view, name="login"),
 #   path('verify-signature/<int:invoice_id>/', VerifySignatureAPIView.as_view(), name='verify-signature'),
]