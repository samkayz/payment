# Generated by Django 3.0.2 on 2020-01-16 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_balance_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='zip_code',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]