# Generated by Django 5.0.2 on 2024-08-25 19:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_transaction_transaction_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(blank=True, choices=[('completed', 'completed'), ('incomplete', 'incomplete'), ('pending', 'pending'), ('failed', 'failed')], max_length=64, null=True),
        ),
        migrations.CreateModel(
            name='PendingCoinSale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coin_amount', models.FloatField(blank=True, default='0.0', null=True)),
                ('coin_type', models.CharField(blank=True, max_length=10, null=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.client')),
            ],
        ),
        migrations.CreateModel(
            name='PendingGiftCardSale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('giftcard_type', models.CharField(blank=True, default='No Found', max_length=20, null=True)),
                ('giftcard_amount', models.FloatField(blank=True, default='0.0', null=True)),
                ('giftcard_number', models.CharField(blank=True, default='No number', max_length=100, null=True)),
                ('country', models.CharField(blank=True, default='United States', max_length=30, null=True)),
                ('amount', models.FloatField(blank=True, default='0.0', null=True)),
                ('front_pic', models.ImageField(blank=True, null=True, upload_to='')),
                ('back_pic', models.ImageField(blank=True, null=True, upload_to='')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.client')),
            ],
        ),
    ]
