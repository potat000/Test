# Generated by Django 2.2.7 on 2019-11-06 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_deploy_mode'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deploy',
            old_name='build',
            new_name='app',
        ),
    ]