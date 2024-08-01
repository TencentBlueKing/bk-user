# Generated by Django 3.2.25 on 2024-07-31 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0006_alter_tenantuser_time_zone'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbuiltinfield',
            name='display_name_en_us',
            field=models.CharField(max_length=128, null=True, unique=True, verbose_name='展示用名称'),
        ),
        migrations.AddField(
            model_name='userbuiltinfield',
            name='display_name_zh_cn',
            field=models.CharField(max_length=128, null=True, unique=True, verbose_name='展示用名称'),
        ),
    ]