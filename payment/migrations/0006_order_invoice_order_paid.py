# Generated by Django 5.1 on 2024-09-14 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_order_date_shipped'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='invoice',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
