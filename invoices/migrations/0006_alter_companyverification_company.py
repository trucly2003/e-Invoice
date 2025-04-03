# Generated by Django 5.1.7 on 2025-04-02 06:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0005_invoiceupload_cloudinary_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyverification',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verifications', to='invoices.company'),
        ),
    ]
