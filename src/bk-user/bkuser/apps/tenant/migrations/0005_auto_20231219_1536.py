# Generated by Django 3.2.20 on 2023-12-19 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0004_auto_20231129_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenantusercustomfield',
            name='manager_editable',
            field=models.BooleanField(default=True, verbose_name='租户管理员是否可重复编辑'),
        ),
        migrations.AddField(
            model_name='tenantusercustomfield',
            name='personal_center_editable',
            field=models.BooleanField(default=False, verbose_name='是否在个人中心可编辑'),
        ),
        migrations.AddField(
            model_name='tenantusercustomfield',
            name='personal_center_visible',
            field=models.BooleanField(default=False, verbose_name='是否在个人中心可见'),
        ),
        migrations.AlterField(
            model_name='tenantusercustomfield',
            name='required',
            field=models.BooleanField(default=False, verbose_name='是否必填'),
        ),
    ]
