# Generated by Django 4.2.4 on 2023-08-30 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_bookinstance_borrower'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='biography',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
