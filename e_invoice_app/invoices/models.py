from django.db import models


class Seller(models.Model):
    name = models.CharField(max_length=255)
    tax_code = models.CharField(max_length=50)
    address = models.TextField()
    phone = models.CharField(max_length=11)
    bank_account = models.CharField(max_length=100)


class Buyer(models.Model):
    name = models.CharField(max_length=255)
    tax_code = models.CharField(max_length=50)
    address = models.TextField()
    phone = models.CharField(max_length=11)
    bank_account = models.CharField(max_length=100)


class Email(models.Model):
    sender = models.EmailField()
    recipient = models.EmailField()
    received_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return f"Email từ {self.sender} - {self.received_date }"


class EmailInvoice(models.Model):  # Trích xuất từ email
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    invoice_lookup_link = models.URLField(null=True, blank=True)  # Cập nhật
    invoice_code = models.CharField(max_length=100, null=True, blank=True)  # Cập nhật
    template_number = models.CharField(max_length=10, null=True, blank=True)  # Cập nhật
    symbol = models.CharField(max_length=20, null=True, blank=True)  # Cập nhật
    invoice_number = models.CharField(max_length=50, null=True, blank=True)  # Cập nhật
    invoice_date = models.DateField(null=True, blank=True)  # Cập nhật
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(max_length=50, null=True, blank=True)  # Cập nhật
    ref_no = models.CharField(max_length=100, null=True, blank=True)  # Cập nhật
    bl_number = models.CharField(max_length=100, null=True, blank=True)  # Cập nhật
    bank_account_vnd = models.CharField(max_length=100, null=True, blank=True)
    bank_account_usd = models.CharField(max_length=100, null=True, blank=True)
    swift_code = models.CharField(max_length=20, null=True, blank=True)  # Cập nhật

    def __str__(self):
        return f"Hóa đơn {self.invoice_number} - {self.company_name}"

    def __str__(self):
        return f"Hóa đơn {self.invoice_number} - {self.company_name}"


class Invoice(models.Model):  # Trích xuất từ file xml, pdf
    email_invoice = models.ForeignKey(
        EmailInvoice, on_delete=models.CASCADE
    )  # khóa đến bảng invoicedata
    serial = models.CharField(max_length=50)
    issue_date = models.DateField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    source_type = models.CharField(
        max_length=10, choices=[("XML", "XML"), ("PDF", "PDF")]
    )


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2)


class ExtractedData(models.Model):
    email_invoice = models.ForeignKey(
        EmailInvoice, on_delete=models.CASCADE, related_name="extracted_data"
    )
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE, related_name="extracted_data"
    )
    source_type = models.CharField(
        max_length=10, choices=[("XML", "XML"), ("PDF", "PDF")]
    )


class Payment(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payments"
    )
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=50)


class Check(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="checks"
    )
    buyer_info = models.TextField()
    seller_info = models.TextField()
    tax_system_check = models.BooleanField(default=False)
    invoice_registered_check = models.BooleanField(default=False)
    digital_signature_check = models.BooleanField(default=False)
