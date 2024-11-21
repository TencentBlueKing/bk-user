# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from typing import List

import pytest
from bkuser.apps.audit.models import OperationAuditRecord
from bkuser.apps.tenant.models import Tenant

from tests.test_utils.auth import create_user
from tests.test_utils.tenant import create_tenant

pytestmark = pytest.mark.django_db


@pytest.fixture
def audit_records(bk_user, default_tenant, other_tenant) -> List[OperationAuditRecord]:
    return [
        OperationAuditRecord.objects.create(
            creator=bk_user.username,
            tenant_id="default",
            operation="create_data_source",
            object_type="data_source",
            object_id="1",
            object_name="DataSource1",
        ),
        OperationAuditRecord.objects.create(
            creator=bk_user.username,
            tenant_id="default",
            operation="delete_data_source",
            object_type="data_source",
            object_id="2",
            object_name="DataSource2",
        ),
        OperationAuditRecord.objects.create(
            creator=bk_user.username,
            tenant_id="default",
            operation="modify_data_source",
            object_type="data_source",
            object_id="3",
            object_name="DataSource3",
        ),
        OperationAuditRecord.objects.create(
            creator=bk_user.username,
            tenant_id="default",
            operation="sync_data_source",
            object_type="data_source",
            object_id="4",
            object_name="DataSource4",
        ),
        OperationAuditRecord.objects.create(
            creator=create_user(other_tenant).username,
            tenant_id="other_tenant",
            operation="sync_data_source",
            object_type="data_source",
            object_id="4",
            object_name="DataSource4",
        ),
    ]


@pytest.fixture
def other_tenant() -> Tenant:
    return create_tenant(tenant_id="other_tenant")
