# Generated by Django 5.0.2 on 2024-03-26 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_pendingcoinpurchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='bank_name',
            field=models.CharField(blank=True, default='Update Your Account', max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='bankaccount_number',
            field=models.CharField(blank=True, default='Update Your Account', max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='home_address',
            field=models.CharField(blank=True, default='Update Your Account', max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='phone_number',
            field=models.CharField(blank=True, default='+234 ****', max_length=64, null=True),
        ),
    ]
