from rest_framework import serializers
from invoices.models import InvoiceUpload, ExtractedInvoice


class InvoiceUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceUpload
        fields = ['id', 'uploaded_by', 'file', 'file_type', 'uploaded_at', 'status']


class ExtractedInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedInvoice
        fields = [
            'id', 'invoice_number', 'invoice_date', 'total_amount',
            'vat_amount', 'grand_total', 'seller', 'buyer'
        ]
