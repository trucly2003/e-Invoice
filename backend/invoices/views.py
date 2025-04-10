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
from invoices.utils.verifySig import check_pdf_signature_windows, extract_text_from_pdf, download_cloud_file_temp

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

        # ✅ Detect file type (PDF or Image)
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and 'pdf' in mime_type:
            upload_obj.file_type = "PDF"
        else:
            upload_obj.file_type = "IMG"
        upload_obj.save()

        try:
            # ✅ OCR text
            text = extract_text_from_pdf(file_path) if upload_obj.file_type == "PDF" else extract_text_from_image(file_path)
            parsed = parse_invoice_by_layout(text)

            # ✅ Seller
            seller, _ = Company.objects.get_or_create(
                tax_code=parsed["seller_tax"],
                defaults={"name": parsed["seller_name"], "address": parsed["seller_address"]}
            )

            # ✅ Buyer (cập nhật nếu có thay đổi)
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
                serial=parsed.get("serial", "")
            )

            # ✅ Upload Cloudinary (giữ local file để dùng pdfsig)
            result = cloudinary.uploader.upload(
                file_path,
                folder="invoices",
                resource_type="raw",
                delivery_type="upload",
                use_filename=True,
                unique_filename=False
            )
            upload_obj.cloudinary_url = result.get("secure_url")
            # ❌ KHÔNG XÓA file local nữa → cần để kiểm thử chữ ký
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

class SignatureVerificationViewSet(viewsets.ModelViewSet):
    queryset = SignatureVerification.objects.all()
    serializer_class = SignatureVerificationSerializer

    @action(detail=True, methods=['post'], url_path='verify')
    def verify_signature(self, request, pk=None):
        try:
            invoice = ExtractedInvoice.objects.get(id=pk)
            upload = invoice.upload

            if not upload:
                return Response({"error": "Không tìm thấy file gốc từ upload."}, status=400)

            # ✅ Ưu tiên dùng file local nếu tồn tại
            pdf_path = None
            if upload.file and upload.file.path and os.path.exists(upload.file.path):
                pdf_path = upload.file.path
                print("📄 Dùng file local:", pdf_path)
            elif upload.cloudinary_url:
                try:
                    pdf_path = download_cloud_file_temp(upload.cloudinary_url)
                    print("☁️ Dùng file cloud:", pdf_path)
                except Exception as e:
                    return Response({"error": f"Lỗi tải từ Cloudinary: {str(e)}"}, status=400)
            else:
                return Response({"error": "Không có file local hoặc cloudinary URL để xử lý."}, status=400)

            # ✅ Kiểm tra loại file
            if upload.file_type == "IMG":
                return Response({"error": "Không áp dụng kiểm tra chữ ký số cho file ảnh."}, status=400)

            # ✅ OCR + kiểm tra chữ ký
            pdf_text = extract_text_from_pdf(pdf_path)
            sig_info = check_pdf_signature_windows(pdf_path)

            matched_name = invoice.seller.name if invoice.seller else ""
            match = sig_info["signer_name"] in pdf_text or sig_info["signer_name"] in matched_name
            status_result = "PASS" if sig_info["status"] == "PASS" and match else "FAIL"

            verification = SignatureVerification.objects.create(
                invoice=invoice,
                signer_name=sig_info["signer_name"],
                status=status_result,
                match_content=match,
                result_detail=sig_info["raw_output"]
            )

            serializer = self.get_serializer(verification)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ExtractedInvoice.DoesNotExist:
            return Response({"error": "Không tìm thấy hóa đơn."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
