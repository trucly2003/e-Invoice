from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets
import mimetypes
import os

from invoices.utils.invoice_parser import parse_invoice_by_layout
from invoices.utils.ocr_utils import extract_text_from_pdf, extract_text_from_image
from .serializers import UploadedFileSerializer, ExtractedInvoiceSerializer, CompanyVerificationSerializer, SignatureVerificationSerializer
from invoices.utils.verifyMasothue import crawl_taxcode_data, verify_company_data
from invoices.utils.verifyHoadondientu import verify_invoice_by_id
from .models import ExtractedInvoice, Company, InvoiceUpload, CompanyVerification, InvoiceVerification, SignatureVerification
from invoices.utils.xml_verifier import verify_signature_from_latest_xml
from invoices.utils.crawl_save_xml import crawl_save_and_verify_xml

import cloudinary.uploader


class UploadInvoiceViewSet(viewsets.ModelViewSet):
    queryset = InvoiceUpload.objects.all()
    serializer_class = UploadedFileSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        upload_obj = serializer.save()
        file_path = upload_obj.file.path

        mime_type, _ = mimetypes.guess_type(file_path)
        upload_obj.file_type = "PDF" if mime_type and 'pdf' in mime_type else "IMG"
        upload_obj.save()

        try:
            raw_text, normalized_text = extract_text_from_pdf(file_path)
            parsed = parse_invoice_by_layout(normalized_text)

            for field in ["seller_name", "seller_address", "buyer_name", "buyer_address"]:
                if parsed.get(field):
                    parsed[field] = parsed[field][:255]

            if parsed.get("ma_tra_cuu"):
                parsed["ma_tra_cuu"] = parsed["ma_tra_cuu"][:50]

            if parsed.get("link_tra_cuu"):
                parsed["link_tra_cuu"] = parsed["link_tra_cuu"][:300]

            # ✅ Seller
            seller, created = Company.objects.get_or_create(
                tax_code=parsed["seller_tax"],
                defaults={"name": parsed["seller_name"], "address": parsed["seller_address"]}
            )
            if not created:
                changed = False
                if seller.name != parsed["seller_name"]:
                    seller.name = parsed["seller_name"]
                    changed = True
                if seller.address != parsed["seller_address"]:
                    seller.address = parsed["seller_address"]
                    changed = True
                if changed:
                    seller.save()

            # ✅ Buyer
            buyer, created = Company.objects.get_or_create(
                tax_code=parsed["buyer_tax"],
                defaults={"name": parsed["buyer_name"], "address": parsed["buyer_address"]}
            )
            if not created:
                changed = False
                if buyer.name != parsed["buyer_name"]:
                    buyer.name = parsed["buyer_name"]
                    changed = True
                if buyer.address != parsed["buyer_address"]:
                    buyer.address = parsed["buyer_address"]
                    changed = True
                if changed:
                    buyer.save()

            # ✅ Create ExtractedInvoice
            invoice = ExtractedInvoice.objects.create(
                upload=upload_obj,
                invoice_number=parsed["invoice_number"],
                invoice_date=parsed["invoice_date"],
                seller=seller,
                buyer=buyer,
                total_amount=parsed["total_amount"],
                vat_amount=parsed["vat_amount"],
                grand_total=parsed["grand_total"],
                serial=parsed.get("serial", "")[:50],
                link_tra_cuu=parsed.get("link_tra_cuu", "")[:300],
                ma_tra_cuu=parsed.get("ma_tra_cuu", "")[:50],
            )

            result = cloudinary.uploader.upload(
                file_path,
                folder="invoices",
                resource_type="raw",
                delivery_type="upload",
                use_filename=True,
                unique_filename=False
            )
            upload_obj.cloudinary_url = result.get("secure_url")
            os.remove(file_path)
            upload_obj.save()

            return Response({
                "message": "✅ Upload và trích xuất thành công.",
                "cloudinary": upload_obj.cloudinary_url,
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "seller": invoice.seller.name,
                "buyer": invoice.buyer.name,
                "total_amount": invoice.total_amount,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"❌ Lỗi xử lý hóa đơn: {str(e)}"}, status=400)


class ExtractedInvoiceViewSet(viewsets.ModelViewSet):
    queryset = ExtractedInvoice.objects.all()
    serializer_class = ExtractedInvoiceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="verify-companies")
    def verify_companies(self, request, pk=None):
        try:
            invoice = self.get_object()
            results = {}

            # Verify Seller
            if invoice.seller:
                seller = invoice.seller
                crawled_seller = crawl_taxcode_data(seller.tax_code)
                seller_status, seller_msg = verify_company_data(seller, crawled_seller)

                seller_verification = CompanyVerification.objects.create(
                    company=seller,
                    invoice=invoice,
                    role="seller",
                    status=seller_status,
                    message=seller_msg,
                    source="masothue"
                )
                results["seller"] = CompanyVerificationSerializer(seller_verification).data

            # Verify Buyer
            if invoice.buyer:
                buyer = invoice.buyer
                crawled_buyer = crawl_taxcode_data(buyer.tax_code)
                buyer_status, buyer_msg = verify_company_data(buyer, crawled_buyer)

                buyer_verification = CompanyVerification.objects.create(
                    company=buyer,
                    invoice=invoice,
                    role="buyer",
                    status=buyer_status,
                    message=buyer_msg,
                    source="masothue"
                )
                results["buyer"] = CompanyVerificationSerializer(buyer_verification).data

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"], url_path="verify")
    def verify_invoice(self, request, pk=None):
        try:
            invoice = self.get_object()
            result = verify_invoice_by_id(invoice.id)

            # Save result to InvoiceVerification
            InvoiceVerification.objects.update_or_create(
                invoice=invoice,
                defaults={
                    "status": result["status"],
                    "result_content": result["result_content"],
                    "source": "hoadondientu"
                }
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InvoiceDownloadViewSet(viewsets.ModelViewSet):
    queryset = ExtractedInvoice.objects.all()
    serializer_class = ExtractedInvoiceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="download-xml")
    def download_xml(self, request, pk=None):
        try:
            invoice = self.get_object()
            crawl_save_and_verify_xml(invoice.id)

            return Response({
                "message": f"✅ Đã tải, upload Cloudinary và lưu XML cho mã: {invoice.ma_tra_cuu}"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"❌ Lỗi khi xử lý XML: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyXMLViewSet(viewsets.ModelViewSet):
    queryset = ExtractedInvoice.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SignatureVerificationSerializer

    @action(detail=True, methods=["post"], url_path="verify-signature")
    def verify_signature(self, request, pk=None):
        try:
            invoice = self.get_object()
        except ExtractedInvoice.DoesNotExist:
            return Response({"error": "Không tìm thấy hóa đơn."}, status=status.HTTP_404_NOT_FOUND)

        result, code = verify_signature_from_latest_xml(invoice)
        return Response(result, status=code)