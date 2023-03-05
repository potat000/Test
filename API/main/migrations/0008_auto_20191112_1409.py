# Generated by Django 2.2.7 on 2019-11-12 05:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0007_auto_20191112_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appservice',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='server',
            name='domain',
            field=models.CharField(max_length=255, unique=True, verbose_name='Domain'),
        ),
        migrations.AlterUniqueTogether(
            name='manager',
            unique_together={('user', 'server')},
        ),
    ]