# Generated by Django 3.2.25 on 2024-07-31 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_source', '0003_auto_20240705_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasourceplugin',
            name='description_en_us',
            field=models.TextField(blank=True, default='', null=True, verbose_name='描述'),
        ),
        migrations.AddField(
            model_name='datasourceplugin',
            name='description_zh_cn',
            field=models.TextField(blank=True, default='', null=True, verbose_name='描述'),
        ),
        migrations.AddField(
            model_name='datasourceplugin',
            name='name_en_us',
            field=models.CharField(max_length=128, null=True, unique=True, verbose_name='数据源插件名称'),
        ),
        migrations.AddField(
            model_name='datasourceplugin',
            name='name_zh_cn',
            field=models.CharField(max_length=128, null=True, unique=True, verbose_name='数据源插件名称'),
        ),
    ]