from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets
from .serializers import UploadedFileSerializer, ExtractedInvoiceSerializer, CompanyVerificationSerializer
from .utils.invoice_parser import extract_invoice_from_file
from invoices.utils.verifyMasothue import crawl_taxcode_data, verify_company_data
from invoices.utils.verifyHoadondientu import verify_invoice_by_id
from .models import ExtractedInvoice, Company, InvoiceUpload


class UploadInvoiceViewSet(viewsets.ModelViewSet):
    queryset = InvoiceUpload.objects.all()
    serializer_class = UploadedFileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            upload_obj = serializer.save()
            cloud_url = upload_obj.file.url

            try:
                invoice = extract_invoice_from_file(upload_obj)
                return Response({
                    "message": "✅ Upload và trích xuất thành công.",
                    "cloudinary": cloud_url,
                    "invoice_id": invoice.id,
                    "invoice_number": invoice.invoice_number,
                    "seller": invoice.seller.name,
                    "buyer": invoice.buyer.name,
                    "total_amount": invoice.total_amount,
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyVerificationViewSet(viewsets.ViewSet):

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk=None):
        try:
            company = Company.objects.get(pk=pk)
            crawled = crawl_taxcode_data(company.tax_code)
            verification = verify_company_data(company, crawled)
            serializer = CompanyVerificationSerializer(verification)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response({"error": "Không tìm thấy công ty"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        try:
            company = Company.objects.get(pk=pk)
            verifications = company.verifications.all().order_by("-verified_at")
            serializer = CompanyVerificationSerializer(verifications, many=True)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response({"error": "Không tìm thấy công ty"}, status=status.HTTP_404_NOT_FOUND)

class ExtractedInvoiceViewSet(viewsets.ModelViewSet):
    queryset = ExtractedInvoice.objects.all()
    serializer_class = ExtractedInvoiceSerializer

    @action(detail=True, methods=["post"], url_path="verify-companies")
    def verify_companies(self, request, pk=None):
        try:
            invoice = self.get_object()
            results = {}

            # 🧾 Xác minh người bán
            if invoice.seller:
                seller = invoice.seller
                crawled_seller = crawl_taxcode_data(seller.tax_code)
                verification_seller = verify_company_data(seller, crawled_seller)
                results["seller_verification"] = CompanyVerificationSerializer(verification_seller).data
            else:
                results["seller_verification"] = {"status": "FAIL", "message": "Invoice không có seller"}

            # 🧾 Xác minh người mua
            if invoice.buyer:
                buyer = invoice.buyer
                crawled_buyer = crawl_taxcode_data(buyer.tax_code)
                verification_buyer = verify_company_data(buyer, crawled_buyer)
                results["buyer_verification"] = CompanyVerificationSerializer(verification_buyer).data
            else:
                results["buyer_verification"] = {"status": "FAIL", "message": "Invoice không có buyer"}

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"], url_path="verify")
    def verify_invoice(self, request, pk=None):
        try:
            invoice_id = int(pk)
            result = verify_invoice_by_id(invoice_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
