from django.contrib.auth.models import User
from rest_framework import serializers
from invoices.models import Company, CompanyVerification, ExtractedInvoice, InvoiceUpload, SignatureVerification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceUpload
        fields = ['file', 'file_type']

    def create(self, validated_data):
        item = InvoiceUpload(**validated_data)
        item.uploaded_by = self.context['request'].user
        return item;





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
