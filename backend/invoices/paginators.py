from rest_framework import  pagination

class UploadInvoicePaginator(pagination.PageNumberPagination):
    page_size = 10