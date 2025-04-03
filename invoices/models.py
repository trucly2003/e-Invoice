from django.db import models
from django.utils import timezone


# ==========================
# Company (Người bán / mua)
# ==========================
class Company(models.Model):
    name = models.CharField(max_length=255)
    tax_code = models.CharField(max_length=50, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bank_account = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} - {self.tax_code}"


# ==========================
# File Hóa đơn người dùng upload
# ==========================
class InvoiceUpload(models.Model):
    uploaded_by = models.CharField(max_length=100)  # Có thể dùng User model sau
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="invoices/", blank=True, null=True)
    cloudinary_url = models.URLField(blank=True, null=True)
    file_type = models.CharField(max_length=10, choices=[("PDF", "PDF"), ("IMG", "Image")])
    status = models.CharField(max_length=50, default="Pending")  # Pending, Processed, Failed

    def __str__(self):
        return f"{self.file.name} - {self.status}"

# ==========================
# Hóa đơn được trích xuất từ file upload
# ==========================
class ExtractedInvoice(models.Model):
    upload = models.OneToOneField(InvoiceUpload, on_delete=models.CASCADE, related_name="extracted")
    serial = models.CharField(max_length=50, blank=True, null=True)
    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField()

    seller = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name="issued_invoices")
    buyer = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name="received_invoices")

    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Hóa đơn {self.invoice_number} - {self.seller}"


# ==========================
# Danh sách sản phẩm trong hóa đơn
# ==========================
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(ExtractedInvoice, on_delete=models.CASCADE, related_name="items")

    item_name = models.TextField()
    unit = models.CharField(max_length=50)
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    amount = models.FloatField()
    tax_rate = models.FloatField(default=0.0)
    tax_amount = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.item_name} ({self.quantity} x {self.unit_price})"


# ==========================
# Kết quả kiểm thử (tổng hợp)
# ==========================
class VerificationResult(models.Model):
    invoice = models.OneToOneField(ExtractedInvoice, on_delete=models.CASCADE, related_name='verification')

    overall_status = models.CharField(
        max_length=10,
        choices=[("PASS", "PASS"), ("FAIL", "FAIL"), ("WARNING", "WARNING")],
        default="FAIL"
    )
    verified_at = models.DateTimeField(default=timezone.now)
    summary = models.TextField(blank=True)

    def __str__(self):
        return f"Kết quả kiểm thử cho hóa đơn #{self.invoice.id} - {self.overall_status}"


# ==========================
# Nhóm kiểm thử (Ví dụ: thông tin người mua, chữ ký số, GDT...)
# ==========================
class VerificationCategory(models.Model):
    result = models.ForeignKey(VerificationResult, on_delete=models.CASCADE, related_name="categories")

    name = models.CharField(max_length=100)  # Ví dụ: "Thông tin người mua", "Chữ ký số"
    status = models.CharField(
        max_length=10,
        choices=[("PASS", "PASS"), ("FAIL", "FAIL"), ("WARNING", "WARNING")],
        default="FAIL"
    )
    message = models.TextField(blank=True)  # Tóm tắt trạng thái nhóm kiểm thử

    def __str__(self):
        return f"[{self.status}] {self.name}"

class CompanyVerification(models.Model):
    STATUS_CHOICES = [("PASS", "PASS"), ("FAIL", "FAIL")]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="verifications")
    verified_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, default="masothue")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"Verification for {self.company.tax_code} at {self.verified_at}"


# ==========================
# Chi tiết từng lỗi nhỏ (dòng kiểm thử trong từng nhóm)
# ==========================
class VerificationDetail(models.Model):
    category = models.ForeignKey(VerificationCategory, on_delete=models.CASCADE, related_name="details")

    label = models.CharField(max_length=255)  # Ví dụ: "Sai tên người mua"
    status = models.CharField(
        max_length=10,
        choices=[("PASS", "PASS"), ("FAIL", "FAIL"), ("WARNING", "WARNING")],
        default="FAIL"
    )
    color = models.CharField(max_length=20, default="black")  # Hỗ trợ UI: red, green, orange

    def __str__(self):
        return f"- {self.label} [{self.status}]"