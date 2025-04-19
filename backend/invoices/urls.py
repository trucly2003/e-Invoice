# invoices/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExtractedInvoiceViewSet, UploadInvoiceViewSet,
    InvoiceDownloadViewSet, VerifyXMLViewSet
)
from .auth_api import login_view, register_view

router = DefaultRouter()
router.register("invoices", ExtractedInvoiceViewSet, basename="invoice")
router.register("upload-invoice", UploadInvoiceViewSet, basename="upload-invoice")
router.register("invoice-download", InvoiceDownloadViewSet, basename="invoice-download")
router.register("verify-xml", VerifyXMLViewSet, basename="verify-xml")

urlpatterns = [
    path("", include(router.urls)),

    # Auth
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),

    # path("invoice-verification/<int:pk>/compare-xml-content/", CompareXMLContentAPIView.as_view(),
    #      name="compare-xml-content"),
    # path("invoice-verification/<int:pk>/verify-xml-signature/", VerifyXMLSignatureAPIView.as_view(),
    #      name="verify-xml-signature"),

]
