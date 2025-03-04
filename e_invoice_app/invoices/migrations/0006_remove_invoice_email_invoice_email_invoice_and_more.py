# Generated by Django 5.1.6 on 2025-03-02 14:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoices", "0005_alter_invoicedata_bl_number_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="invoice",
            name="email",
        ),
        migrations.AddField(
            model_name="invoice",
            name="email_invoice",
            field=models.ForeignKey(
                default=12,
                on_delete=django.db.models.deletion.CASCADE,
                to="invoices.emailinvoice",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="invoice",
            name="source_type",
            field=models.CharField(
                choices=[("XML", "XML"), ("PDF", "PDF")], default=12, max_length=10
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="check",
            name="invoice",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="checks",
                to="invoices.invoice",
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="invoice",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payments",
                to="invoices.invoice",
            ),
        ),
        migrations.RenameModel(
            old_name="InvoiceData",
            new_name="EmailInvoice",
        ),
        migrations.CreateModel(
            name="ExtractedData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "source_type",
                    models.CharField(
                        choices=[("XML", "XML"), ("PDF", "PDF")], max_length=10
                    ),
                ),
                (
                    "email_invoice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extracted_data",
                        to="invoices.emailinvoice",
                    ),
                ),
                (
                    "invoice",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extracted_data",
                        to="invoices.invoice",
                    ),
                ),
            ],
        ),
    ]
