import datetime

import pytest
from django.utils.timezone import now

from bkuser_core.audit.constants import LogInFailReason
from bkuser_core.audit.models import LogIn

pytestmark = pytest.mark.django_db


class TestLoginManager:
    @pytest.mark.parametrize(
        "records,count",
        [
            (
                (
                    # latest success
                    (60 * 60 * 24 * 29, True),
                    (60 * 60 * 24 * 27, False),
                    (60 * 60 * 24 * 26, False),
                    (60 * 60 * 24 * 25, False),
                ),
                3,
            ),
            (
                (
                    # too far
                    (60 * 60 * 24 * 31, True),
                    # latest success
                    (60 * 60 * 24 * 29, True),
                    (60 * 60 * 24 * 27, False),
                    (60 * 60 * 24 * 26, False),
                    (60 * 60 * 24 * 25, False),
                ),
                3,
            ),
            (
                (
                    # too far
                    (60 * 60 * 24 * 32, False),
                    (60 * 60 * 24 * 31, True),
                    # latest success
                    (60 * 60 * 24 * 29, True),
                    (60 * 60 * 24 * 27, False),
                    (60 * 60 * 24 * 26, False),
                ),
                2,
            ),
            (
                (
                    # too far
                    (60 * 60 * 24 * 32, True),
                    (60 * 60 * 24 * 31, True),
                    # no success
                    (60 * 60 * 24 * 29, False),
                    (60 * 60 * 24 * 27, False),
                    (60 * 60 * 24 * 26, False),
                    (60 * 60 * 24 * 26, False),
                ),
                4,
            ),
            (
                (
                    # too far
                    (60 * 60 * 24 * 32, True),
                    (60 * 60 * 24 * 31, True),
                    (60 * 60 * 24 * 31, False),
                    # count start from below
                    (60 * 60 * 24 * 27, False),
                    (60 * 60 * 24 * 26, False),
                    (60 * 60 * 24 * 26, False),
                ),
                3,
            ),
        ],
    )
    def test_latest_failed_count(self, records, count):
        """测试最近登录失败次数"""

        now_time = now()
        for record in records:
            _l = LogIn.objects.create(
                profile_id=1,
                is_success=record[1],
                reason=LogInFailReason.BAD_PASSWORD.value,
            )
            _l.create_time = now_time - datetime.timedelta(seconds=record[0])
            _l.save()

        assert LogIn.objects.latest_failed_count() == count
