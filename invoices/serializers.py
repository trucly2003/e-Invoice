from rest_framework import serializers
from invoices.models import Company, CompanyVerification, ExtractedInvoice, InvoiceUpload, SignatureVerification


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceUpload
        fields = ['file', 'file_type']


class SignatureVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignatureVerification
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "tax_code",
            "address",
        ]


class CompanyVerificationSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = CompanyVerification
        fields = [
            "id",
            "company",
            "verified_at",
            "source",
            "status",
            "message",
        ]


class ExtractedInvoiceSerializer(serializers.ModelSerializer):
    seller = CompanySerializer(read_only=True)
    buyer = CompanySerializer(read_only=True)

    class Meta:
        model = ExtractedInvoice
        fields = [
            "id",
            "serial",
            "invoice_date",
            "total",
            "seller",
            "buyer",
            "crawled_seller",
            "crawled_buyer",
        ]
