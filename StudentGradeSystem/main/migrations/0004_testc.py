# Generated by Django 3.2 on 2023-03-14 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_testa_b'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c', models.CharField(max_length=10)),
                ('d', models.IntegerField()),
            ],
        ),
    ]
