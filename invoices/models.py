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


class CompanyVerification(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="verifications")
    invoice = models.ForeignKey(ExtractedInvoice, on_delete=models.CASCADE, related_name="company_verifications",
                                null=True, blank=True)

    ROLE_CHOICES = [
        ("seller", "Seller"),
        ("buyer", "Buyer")
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=True, blank=True)

    status = models.CharField(max_length=10, choices=[("PASS", "PASS"), ("FAIL", "FAIL")])
    message = models.TextField()
    source = models.CharField(max_length=50, default="masothue")
    verified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.role}] {self.company.name} - {self.status}"

class InvoiceVerification(models.Model):
    invoice = models.ForeignKey(ExtractedInvoice, on_delete=models.CASCADE, related_name="invoice_verification",
                                null=True, blank=True)

    status = models.CharField(max_length=10, choices=[("PASS", "PASS"), ("FAIL", "FAIL")])
    result_content = models.TextField()
    source = models.CharField(max_length=50, default="hoadondientu")
    verified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.status}"

# models.py
class SignatureVerification(models.Model):
    invoice = models.ForeignKey(ExtractedInvoice, on_delete=models.CASCADE, related_name="signature_verification")
    signer_name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=[("PASS", "PASS"), ("FAIL", "FAIL")])
    match_content = models.BooleanField(default=False)
    result_detail = models.TextField()
    verified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.status}"

