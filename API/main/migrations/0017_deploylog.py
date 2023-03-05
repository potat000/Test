# Generated by Django 2.2.7 on 2021-03-04 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20200521_1201'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeployLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=255, null=True, verbose_name='IP')),
                ('platformSystem', models.CharField(max_length=255, null=True, verbose_name='Platform system')),
                ('platformVersion', models.CharField(max_length=255, null=True, verbose_name='Platform version')),
                ('username', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Usernae')),
                ('fullCommand', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Full command')),
                ('server', models.CharField(db_index=True, max_length=255, null=True, verbose_name='server')),
                ('command', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Command')),
                ('options', models.CharField(max_length=255, null=True, verbose_name='Options')),
                ('output', models.TextField(null=True, verbose_name='Output')),
                ('stdout', models.TextField(null=True, verbose_name='Stdout')),
                ('stderr', models.TextField(null=True, verbose_name='Stderr')),
            ],
        ),
    ]