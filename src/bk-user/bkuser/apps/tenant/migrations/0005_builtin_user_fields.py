from django.db import migrations


def forwards_func(apps, schema_editor):
    """初始化用户内置字段"""

    UserBuiltinField = apps.get_model("tenant", "UserBuiltinField")
    fields = [
        UserBuiltinField(
            name="username",
            display_name="用户名",
            data_type="string",
            required=True,
            unique=True,
        ),
        UserBuiltinField(
            name="full_name",
            display_name="姓名",
            data_type="string",
            required=True,
            unique=False,
        ),
        UserBuiltinField(
            name="email",
            display_name="邮箱",
            data_type="string",
            required=False,
            unique=False,
        ),
        UserBuiltinField(
            name="phone",
            display_name="手机号",
            data_type="string",
            required=False,
            unique=False,
        ),
        UserBuiltinField(
            name="phone_country_code",
            display_name="手机国际区号",
            data_type="string",
            required=False,
            unique=False,
        )
    ]
    UserBuiltinField.objects.bulk_create(fields)


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0004_auto_20230914_2009'),
    ]

    operations = [
        migrations.RunPython(forwards_func)
    ]
