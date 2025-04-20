from django.contrib.auth.models import User
from rest_framework import serializers
from invoices.models import Company, CompanyVerification, ExtractedInvoice, InvoiceUpload, SignatureVerification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "tax_code",
            "address",
        ]

class ExtractedInvoiceSerializer(serializers.ModelSerializer):
    seller = CompanySerializer(read_only=True)
    buyer = CompanySerializer(read_only=True)

    class Meta:
        model = ExtractedInvoice
        fields = [
            "id",
            "invoice_number",
            "invoice_date",
            'vat_amount',
            'grand_total',
            "total_amount",
            "seller",
            "buyer"
        ]

class UploadedFileSerializer(serializers.ModelSerializer):
    extracted = ExtractedInvoiceSerializer(many=True, read_only=True)
    class Meta:
        model = InvoiceUpload
        fields = ['id', 'file', 'file_type', 'extracted', 'status', 'uploaded_at' ]
        read_only_fields = [ 'id', 'status', 'extracted', 'uploaded_at']


    def create(self, validated_data):
        item = InvoiceUpload(**validated_data)
        item.uploaded_by = self.context['request'].user
        return item;







class SignatureVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignatureVerification
        fields = '__all__'




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



