# Generated by Django 5.1.7 on 2025-04-20 02:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('tax_code', models.CharField(max_length=50, unique=True)),
                ('address', models.TextField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('bank_account', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ExtractedInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial', models.CharField(blank=True, max_length=50, null=True)),
                ('invoice_number', models.CharField(max_length=100)),
                ('invoice_date', models.DateField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('vat_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=15)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=15)),
                ('ma_tra_cuu', models.CharField(blank=True, max_length=50, null=True)),
                ('link_tra_cuu', models.URLField(blank=True, max_length=300, null=True)),
                ('xml_filename', models.CharField(blank=True, max_length=512, null=True)),
                ('buyer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_invoices', to='invoices.company')),
                ('seller', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issued_invoices', to='invoices.company')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, choices=[('seller', 'Seller'), ('buyer', 'Buyer')], max_length=10, null=True)),
                ('status', models.CharField(choices=[('PASS', 'PASS'), ('FAIL', 'FAIL')], max_length=10)),
                ('message', models.TextField()),
                ('source', models.CharField(default='masothue', max_length=50)),
                ('verified_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verifications', to='invoices.company')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_verifications', to='invoices.extractedinvoice')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.TextField()),
                ('unit', models.CharField(max_length=50)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.FloatField()),
                ('amount', models.FloatField()),
                ('tax_rate', models.FloatField(default=0.0)),
                ('tax_amount', models.FloatField(default=0.0)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='invoices.extractedinvoice')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='invoices/pdf_files/')),
                ('cloudinary_url', models.URLField(blank=True, null=True)),
                ('file_type', models.CharField(choices=[('PDF', 'PDF'), ('IMG', 'Image')], max_length=10)),
                ('status', models.CharField(default='Pending', max_length=50)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_invoices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='extractedinvoice',
            name='upload',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='extracted', to='invoices.invoiceupload'),
        ),
        migrations.CreateModel(
            name='InvoiceVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PASS', 'PASS'), ('FAIL', 'FAIL')], max_length=10)),
                ('result_content', models.TextField()),
                ('source', models.CharField(default='hoadondientu', max_length=50)),
                ('verified_at', models.DateTimeField(auto_now_add=True)),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoice_verification', to='invoices.extractedinvoice')),
            ],
        ),
        migrations.CreateModel(
            name='SignatureVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signer_name', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('PASS', 'PASS'), ('FAIL', 'FAIL')], max_length=10)),
                ('match_content', models.BooleanField(default=False)),
                ('result_detail', models.TextField()),
                ('verified_at', models.DateTimeField(auto_now_add=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signature_verification', to='invoices.extractedinvoice')),
            ],
        ),
        migrations.CreateModel(
            name='VerifiedXMLInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=50)),
                ('invoice_date', models.DateField(blank=True, null=True)),
                ('seller_tax_code', models.CharField(max_length=20)),
                ('buyer_tax_code', models.CharField(max_length=20)),
                ('total_amount', models.FloatField(blank=True, null=True)),
                ('vat_amount', models.FloatField(blank=True, null=True)),
                ('grand_total', models.FloatField(blank=True, null=True)),
                ('cloudinary_url', models.URLField(blank=True, null=True)),
                ('raw_xml', models.TextField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=10, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('local_xml_path', models.TextField(blank=True, null=True)),
                ('verified_at', models.DateTimeField(auto_now=True)),
                ('invoice', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='invoices.extractedinvoice')),
            ],
        ),
    ]
