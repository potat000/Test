# Generated by Django 3.2 on 2023-03-14 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_testa_b'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testa',
            name='b',
        ),
    ]