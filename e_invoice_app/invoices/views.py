from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from invoices.models import InvoiceUpload
from invoices.serializers import InvoiceUploadSerializer
from invoices.utils.invoice_parser import extract_invoice_from_file


class InvoiceUploadViewSet(viewsets.ModelViewSet):
    queryset = InvoiceUpload.objects.all()
    serializer_class = InvoiceUploadSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        file_type = request.data.get("file_type")
        uploaded_by = request.data.get("uploaded_by", "anonymous")

        if not file or file_type not in ["PDF", "IMG"]:
            return Response({"error": "Thiếu file hoặc file_type không hợp lệ."}, status=400)

        upload_obj = InvoiceUpload.objects.create(
            file=file,
            file_type=file_type,
            uploaded_by=uploaded_by,
            status="Processing"
        )

        try:
            invoice = extract_invoice_from_file(upload_obj)
            upload_obj.status = "Processed"
            upload_obj.save()

            return Response({
                "message": "Upload và trích xuất thành công.",
                "cloudinary_url": upload_obj.file.url,
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "seller": invoice.seller.name,
                "buyer": invoice.buyer.name,
                "total_amount": float(invoice.total_amount)
            }, status=201)

        except Exception as e:
            upload_obj.status = "Failed"
            upload_obj.save()
            return Response({"error": str(e)}, status=500)
