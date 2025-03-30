from rest_framework.routers import DefaultRouter
from invoices.views import InvoiceUploadViewSet

router = DefaultRouter()
router.register(r'upload-invoice', InvoiceUploadViewSet, basename='upload-invoice')

urlpatterns = router.urls
