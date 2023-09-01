from typing import Optional

from bkuser.apps.tenant.models import Tenant

# 默认租户 ID & 名称
DEFAULT_TENANT = "default"


def create_tenant(tenant_id: Optional[str] = DEFAULT_TENANT) -> Tenant:
    tenant, _ = Tenant.objects.get_or_create(
        id=tenant_id,
        defaults={"name": tenant_id, "is_default": bool(tenant_id == DEFAULT_TENANT)},
    )
    return tenant
