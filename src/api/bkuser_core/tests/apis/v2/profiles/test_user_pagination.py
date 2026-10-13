# -*- coding: utf-8 -*-
"""v2 用户列表限量、去重分页的回归测试。

查询会在测试数据库中真实执行；仅替换与分页无关的外部配置读取，
过滤、计数、切片及关系加载均使用实际 ORM 和 SQL。
"""

from types import SimpleNamespace

import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db.models import Q
from django.test.utils import CaptureQueriesContext
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from bkuser_core.apis.v2.user_pagination import UserResultsPagination
from bkuser_core.common.error_codes import CoreAPIError
from bkuser_core.departments.models import Department
from bkuser_core.departments.v2.views import DepartmentViewSet
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.v2.views import ProfileViewSet

pytestmark = pytest.mark.django_db

TEST_CATEGORY = 987654


@pytest.fixture(autouse=True)
def pagination_settings(settings, monkeypatch):
    settings.ENABLE_DEFERRED_PAGINATION = False
    settings.DEFERRED_PAGINATION_MIN_OFFSET = 1
    settings.USER_LIST_NO_PAGE_LIMIT = 2
    settings.MAX_PAGE_SIZE = 10000
    settings.ENABLE_PROFILE_SENSITIVE_FILTER = False
    settings.CACHES = {
        name: {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": f"user-pagination-tests-{name}",
        }
        for name in ("default", "locmem", "verification_code")
    }
    for module in (
        "bkuser_core.profiles.v2.views",
        "bkuser_core.profiles.v2.filters",
        "bkuser_core.departments.v2.views",
    ):
        monkeypatch.setattr(f"{module}.get_default_category_domain_from_local_cache", lambda: "default.local")
    monkeypatch.setattr("bkuser_core.profiles.v2.serializers.get_extras_default_from_local_cache", lambda: {})


@pytest.fixture
def users():
    # 测试只验证读取路径，批量创建可以避开与用户写入相关的保存钩子。
    Profile.objects.bulk_create(
        [
            Profile(
                username=f"pagination-user-{number}",
                display_name=f"Name {number // 2}",
                domain="default.local",
                category_id=TEST_CATEGORY,
                code=f"pagination-code-{number}",
                extras={"test": number},
            )
            for number in range(4)
        ]
    )
    return list(Profile.objects.filter(category_id=TEST_CATEGORY).order_by("id"))


@pytest.fixture
def organization(users):
    root = Department.objects.create(name="pagination-root", category_id=TEST_CATEGORY, code="pagination-root")
    first = Department.objects.create(
        name="pagination-333", parent=root, category_id=TEST_CATEGORY, code="pagination-333"
    )
    root.refresh_from_db()
    second = Department.objects.create(
        name="pagination-444", parent=root, category_id=TEST_CATEGORY, code="pagination-444"
    )
    root.profiles.add(users[0])
    first.profiles.add(users[1])
    second.profiles.add(users[1], users[2])
    root.refresh_from_db()
    return SimpleNamespace(root=root, first=first, second=second)


def make_request(**params):
    return Request(APIRequestFactory().get("/api/v2/profiles/", params))


def user_queryset():
    return Profile.objects.filter(category_id=TEST_CATEGORY, enabled=True)


def call_profile_list(raw_response=True, **params):
    view = ProfileViewSet.as_view(
        {"get": "list"}, authentication_classes=[], permission_classes=[], throttle_classes=[]
    )
    headers = {django_settings.FORCE_RAW_RESPONSE_HEADER: "true"} if raw_response else {}
    return view(APIRequestFactory(**headers).get("/api/v2/profiles/", params))


def call_department_profiles(department, raw_response=True, **params):
    view = DepartmentViewSet.as_view(
        {"get": "get_profiles"}, authentication_classes=[], permission_classes=[], throttle_classes=[]
    )
    headers = {django_settings.FORCE_RAW_RESPONSE_HEADER: "true"} if raw_response else {}
    return view(
        APIRequestFactory(**headers).get(f"/api/v2/departments/{department.pk}/profiles/", params),
        lookup_value=str(department.pk),
    )


@pytest.mark.parametrize("enabled", [False, True])
def test_multidepartment_filter_deduplicates_before_count_and_page(users, organization, settings, enabled):
    settings.ENABLE_DEFERRED_PAGINATION = enabled
    queryset = user_queryset().filter(departments__in=[organization.first, organization.second]).order_by("id")
    for number, expected in ((1, users[1]), (2, users[2])):
        paginator = UserResultsPagination()
        rows = paginator.paginate_queryset(queryset, make_request(page=number, page_size=1))
        assert [row.pk for row in rows] == [expected.pk]
        assert paginator.get_paginated_response([]).data["count"] == 2
    with pytest.raises(NotFound):
        UserResultsPagination().paginate_queryset(queryset, make_request(page=3, page_size=1))


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("ordering", ["id", "-id"])
def test_deferred_and_normal_queries_return_identical_order(users, settings, enabled, ordering):
    settings.ENABLE_DEFERRED_PAGINATION = enabled
    queryset = user_queryset().order_by(ordering)
    expected = users if ordering == "id" else list(reversed(users))
    paginator = UserResultsPagination()
    with CaptureQueriesContext(connection) as captured:
        rows = paginator.paginate_queryset(queryset, make_request(page=2, page_size=2))
    assert [row.pk for row in rows] == [row.pk for row in expected[2:4]]
    assert paginator.page.paginator.count == 4
    data_queries = [
        q["sql"]
        for q in captured
        if q["sql"].lstrip().upper().startswith("SELECT") and "COUNT(" not in q["sql"].upper()
    ]
    assert len(data_queries) == (2 if enabled else 1)


def test_recommended_offset_threshold_uses_effective_offset(users, settings):
    settings.ENABLE_DEFERRED_PAGINATION = True
    settings.DEFERRED_PAGINATION_MIN_OFFSET = 20000
    paginator = UserResultsPagination()
    id_ordered = user_queryset().order_by("id")

    # 阈值比较的是实际 OFFSET，不是页码或匹配用户总数。
    assert not paginator._can_defer(id_ordered, 19999)
    assert paginator._can_defer(id_ordered, 20000)
    assert not paginator._can_defer(user_queryset().order_by("display_name"), 20000)

    settings.ENABLE_DEFERRED_PAGINATION = False
    assert not paginator._can_defer(id_ordered, 20000)


def test_join_cross_product_and_or_conditions_still_yield_unique_users(users, organization):
    users[1].leader.add(users[0], users[3])
    queryset = (
        user_queryset()
        .filter(Q(username=users[1].username) | Q(departments__name__startswith="pagination-"))
        .filter(leader__in=[users[0], users[3]])
    )
    paginator = UserResultsPagination()
    rows = paginator.paginate_queryset(queryset, make_request(page_size=1))
    assert [row.pk for row in rows] == [users[1].pk]
    assert paginator.page.paginator.count == 1


def test_non_id_ordering_keeps_order_and_adds_stable_tie_breaker(users, settings):
    settings.ENABLE_DEFERRED_PAGINATION = True
    paginator = UserResultsPagination()
    rows = paginator.paginate_queryset(user_queryset().order_by("-display_name"), make_request(page=2, page_size=2))
    assert [row.pk for row in rows] == [users[0].pk, users[1].pk]
    assert paginator.page.paginator.count == 4


@pytest.mark.parametrize("unpaginated", [False, True])
def test_best_match_extra_select_order_survives_id_projection(users, settings, unpaginated):
    settings.ENABLE_DEFERRED_PAGINATION = True
    settings.USER_LIST_NO_PAGE_LIMIT = 4
    for user, username in zip(users, ["longest-name-in-sample", "x", "aa", "bbb"]):
        Profile.objects.filter(pk=user.pk).update(username=username)
    queryset = (
        user_queryset().extra(select={"lookup_field_length": "LENGTH(username)"}).order_by("lookup_field_length")
    )
    request = make_request(no_page="true") if unpaginated else make_request(page=2, page_size=2)
    rows = UserResultsPagination().paginate_queryset(queryset, request)
    expected = [users[1], users[2], users[3], users[0]] if unpaginated else [users[3], users[0]]
    assert [row.pk for row in rows] == [user.pk for user in expected]


@pytest.mark.parametrize("ordering", ["departments", "-departments", "leader", "leader__username"])
def test_multivalued_ordering_is_rejected(users, ordering):
    with pytest.raises(CoreAPIError) as exc:
        UserResultsPagination().paginate_queryset(user_queryset().order_by(ordering), make_request())
    assert "多值部门或上级关系字段" in exc.value.message


@pytest.mark.parametrize("page", ["0", "-1", "not-a-page", "99"])
def test_invalid_and_out_of_range_pages_keep_not_found(users, page):
    with pytest.raises(NotFound):
        UserResultsPagination().paginate_queryset(user_queryset(), make_request(page=page, page_size=2))


def test_last_page_and_empty_first_page(users, settings):
    settings.ENABLE_DEFERRED_PAGINATION = True
    paginator = UserResultsPagination()
    rows = paginator.paginate_queryset(user_queryset(), make_request(page="last", page_size=3))
    assert [row.pk for row in rows] == [users[-1].pk]
    assert paginator.page.number == 2
    empty = UserResultsPagination()
    assert empty.paginate_queryset(user_queryset().filter(pk=-1), make_request()) == []
    assert empty.get_paginated_response([]).data == {"count": 0, "results": []}


@pytest.mark.parametrize("no_page", ["true", "1"])
def test_no_page_limit_counts_unique_users_not_join_rows(users, organization, settings, no_page):
    settings.USER_LIST_NO_PAGE_LIMIT = 1
    queryset = user_queryset().filter(pk=users[1].pk, departments__in=[organization.first, organization.second])
    paginator = UserResultsPagination()
    rows = paginator.paginate_queryset(queryset, make_request(no_page=no_page))
    assert [row.pk for row in rows] == [users[1].pk]
    assert paginator.get_paginated_response([{"id": users[1].pk}]).data == [{"id": users[1].pk}]


def test_no_page_over_limit_rejects_before_loading_profiles_or_relations(users, organization):
    queryset = user_queryset().prefetch_related("departments", "leader")
    with CaptureQueriesContext(connection) as captured, pytest.raises(CoreAPIError) as exc:
        UserResultsPagination().paginate_queryset(queryset, make_request(no_page="true"))
    assert "no_page" in exc.value.message
    assert len(captured) == 1
    sql = captured[0]["sql"].upper()
    assert "LIMIT 3" in sql
    assert "COUNT(" not in sql
    assert "DEPARTMENTS_DEPARTMENT" not in sql
    assert "EMAIL" not in sql


def test_no_page_exact_limit_and_empty_result(users):
    paginator = UserResultsPagination()
    rows = paginator.paginate_queryset(
        user_queryset().filter(pk__in=[u.pk for u in users[:2]]), make_request(no_page="true")
    )
    assert [row.pk for row in rows] == [u.pk for u in users[:2]]
    assert UserResultsPagination().paginate_queryset(user_queryset().filter(pk=-1), make_request(no_page="true")) == []


def test_page_size_respects_environment_limit_without_a_hidden_hard_limit(settings):
    settings.MAX_PAGE_SIZE = 999999
    assert UserResultsPagination().get_page_size(make_request(page_size=999999)) == 999999
    settings.MAX_PAGE_SIZE = 2
    assert UserResultsPagination().get_page_size(make_request(page_size=3)) == 2
    assert UserResultsPagination().get_page_size(make_request()) == 50


@pytest.mark.parametrize("page_size", [0, -1, "not-a-number"])
def test_invalid_page_size_keeps_historical_default(page_size):
    assert UserResultsPagination().get_page_size(make_request(page_size=page_size)) == 50


def test_no_page_limit_is_independent_from_normal_page_size(users, settings):
    settings.USER_LIST_NO_PAGE_LIMIT = 3
    settings.MAX_PAGE_SIZE = 1
    rows = UserResultsPagination().paginate_queryset(
        user_queryset().filter(pk__in=[user.pk for user in users[:3]]),
        make_request(no_page="true"),
    )
    assert [row.pk for row in rows] == [user.pk for user in users[:3]]


@pytest.mark.parametrize("invalid_limit", [0, -1, True, "1000"])
def test_invalid_limit_does_not_allow_unbounded_no_page(users, settings, invalid_limit):
    settings.USER_LIST_NO_PAGE_LIMIT = invalid_limit
    with pytest.raises(ImproperlyConfigured):
        UserResultsPagination().paginate_queryset(user_queryset(), make_request(no_page="true"))


def test_user_leaving_result_between_two_queries_recalculates_offset_once(users, settings):
    settings.ENABLE_DEFERRED_PAGINATION = True
    changed = []

    def disable_before_full_fetch(execute, sql, params, many, context):
        if not changed and sql.lstrip().upper().startswith("SELECT") and " IN (" in sql.upper():
            changed.append(True)
            Profile.objects.filter(pk=users[1].pk).update(enabled=False)
        return execute(sql, params, many, context)

    paginator = UserResultsPagination()
    with connection.execute_wrapper(disable_before_full_fetch):
        rows = paginator.paginate_queryset(user_queryset(), make_request(page=2, page_size=1))
    assert changed == [True]
    assert [row.pk for row in rows] == [users[2].pk]
    assert paginator.page.paginator.count == 3


@pytest.mark.parametrize("fields", ["id", "id,departments", "departments,leader"])
def test_profile_endpoint_deduplicates_with_or_without_relationship_fields(users, organization, fields):
    response = call_profile_list(
        lookup_field="departments__name",
        exact_lookups=f"{organization.first.name},{organization.second.name}",
        fields=fields,
        page_size=1,
    )
    assert response.status_code == 200
    assert response.data["count"] == 2
    assert len(response.data["results"]) == 1
    row = response.data["results"][0]
    assert set(row) == set(fields.split(","))
    if "id" in row:
        assert row["id"] == users[1].pk
    if "departments" in row:
        assert {department["id"] for department in row["departments"]} == {
            organization.first.pk,
            organization.second.pk,
        }


@pytest.mark.parametrize("enabled", [False, True])
def test_distinct_count_projects_only_user_pk_when_response_contains_wide_fields(
    users, organization, settings, enabled
):
    settings.ENABLE_DEFERRED_PAGINATION = enabled
    with CaptureQueriesContext(connection) as captured:
        response = call_profile_list(
            lookup_field="departments__name",
            exact_lookups=f"{organization.first.name},{organization.second.name}",
            fields="id,extras,logo",
            page=2,
            page_size=1,
        )
    assert response.status_code == 200
    # 三条命中关系实际只对应两个用户；普通分页和延迟关联的第二页都必须先去重再 COUNT/LIMIT。
    assert response.data["count"] == 2
    assert response.data["results"] == [{"id": users[2].pk, "extras": {"test": 2}, "logo": None}]
    count_queries = [query["sql"].upper() for query in captured if "COUNT(" in query["sql"].upper()]
    assert len(count_queries) == 1
    count_sql = count_queries[0]
    assert "SELECT DISTINCT" in count_sql
    assert "PROFILES_PROFILE" in count_sql
    assert "DEPARTMENTS_DEPARTMENT_PROFILES" in count_sql
    # 页面仍可返回 JSON/文本大字段，但唯一用户 COUNT 不应把这些字段带入 DISTINCT 子查询。
    assert "EXTRAS" not in count_sql
    assert "LOGO" not in count_sql
    assert "ORDER BY" not in count_sql


def test_no_page_endpoint_returns_one_user_with_nested_relationships(users, organization, settings):
    settings.USER_LIST_NO_PAGE_LIMIT = 1
    response = call_profile_list(
        no_page="true", lookup_field="id", exact_lookups=users[1].pk, fields="id,departments,leader"
    )
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == users[1].pk
    assert {department["id"] for department in response.data[0]["departments"]} == {
        organization.first.pk,
        organization.second.pk,
    }
    assert response.data[0]["leader"] == []


@pytest.mark.parametrize("for_sync", [False, True])
@pytest.mark.parametrize("unpaginated", [False, True])
def test_default_fields_and_sync_serializer_are_preserved(users, organization, for_sync, unpaginated):
    params = {"lookup_field": "id", "exact_lookups": users[1].pk}
    if for_sync:
        params["for_sync"] = "1"
    if unpaginated:
        params["no_page"] = "true"
    response = call_profile_list(**params)
    assert response.status_code == 200
    row = response.data[0] if unpaginated else response.data["results"][0]
    assert row["id"] == users[1].pk
    assert row["username"] == users[1].username
    assert row["extras"] == {"test": 1}
    if for_sync:
        assert row["code"] == users[1].code
        assert set(row["departments"]) == {organization.first.code, organization.second.code}
    else:
        assert {department["id"] for department in row["departments"]} == {
            organization.first.pk,
            organization.second.pk,
        }


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("recursive", [False, True])
def test_department_endpoint_preserves_recursive_scope_and_unique_users(
    users, organization, settings, enabled, recursive
):
    settings.ENABLE_DEFERRED_PAGINATION = enabled
    response = call_department_profiles(organization.root, recursive=str(recursive).lower(), page_size=2)
    assert response.status_code == 200
    expected = [users[2].pk, users[1].pk] if recursive else [users[0].pk]
    assert [row["id"] for row in response.data["results"]] == expected
    assert response.data["count"] == (3 if recursive else 1)
    if recursive:
        second = call_department_profiles(organization.root, recursive="true", page=2, page_size=2)
        assert [row["id"] for row in second.data["results"]] == [users[0].pk]


def test_department_no_page_is_bounded_and_keeps_nested_relationships(users, organization):
    too_large = call_department_profiles(organization.root, recursive="true", no_page="true")
    assert too_large.status_code == 400
    response = call_department_profiles(organization.second, recursive="true", no_page="true")
    assert response.status_code == 200
    assert [row["id"] for row in response.data] == [users[2].pk, users[1].pk]
    assert isinstance(response.data[1]["departments"], list)
    assert {department["id"] for department in response.data[1]["departments"]} == {
        organization.first.pk,
        organization.second.pk,
    }


@pytest.mark.parametrize("raw_response", [False, True])
@pytest.mark.parametrize("endpoint", ["profiles", "department_profiles"])
def test_no_page_limit_error_obeys_existing_raw_and_enterprise_error_contracts(
    users, organization, raw_response, endpoint
):
    if endpoint == "profiles":
        response = call_profile_list(
            raw_response=raw_response,
            no_page="true",
            lookup_field="category_id",
            exact_lookups=TEST_CATEGORY,
            fields="id",
        )
    else:
        response = call_department_profiles(
            organization.root, raw_response=raw_response, recursive="true", no_page="true"
        )
    if raw_response:
        assert response.status_code == 400
        assert response.data["code"] == "QUERY_PARAMS_ERROR"
        message = response.data["detail"]
    else:
        assert response.status_code == 200
        assert response.data["result"] is False
        assert response.data["code"] != 0
        assert response.data["data"] is None
        message = response.data["message"]
    assert "no_page" in message
    assert "page/page_size" in message
    assert "2" in message
    assert "ErrorDetail" not in message


@pytest.mark.parametrize("raw_response", [False, True])
def test_relation_order_error_obeys_existing_error_contract(users, raw_response):
    response = call_profile_list(
        raw_response=raw_response,
        fields="id",
        ordering="departments",
        lookup_field="category_id",
        exact_lookups=TEST_CATEGORY,
    )
    if raw_response:
        assert response.status_code == 400
        assert response.data["code"] == "QUERY_PARAMS_ERROR"
        message = response.data["detail"]
    else:
        assert response.status_code == 200
        assert response.data["result"] is False
        assert response.data["code"] != 0
        message = response.data["message"]
    assert "ordering" in message
    assert "id" in message
    assert "ErrorDetail" not in message


@pytest.mark.parametrize("raw_response", [False, True])
def test_no_page_unsupported_field_reports_error_instead_of_silently_dropping_code(users, raw_response):
    response = call_profile_list(
        raw_response=raw_response,
        no_page="true",
        fields="id,code",
        lookup_field="id",
        exact_lookups=users[0].pk,
    )
    if raw_response:
        assert response.status_code == 400
        assert response.data["code"] == "QUERY_PARAMS_ERROR"
        message = response.data["detail"]
    else:
        assert response.status_code == 200
        assert response.data["result"] is False
        assert response.data["code"] != 0
        assert response.data["data"] is None
        message = response.data["message"]
    assert "fields" in message
    assert "code" in message
    assert "ErrorDetail" not in message


def test_no_page_for_sync_still_supports_explicit_code_field(users):
    response = call_profile_list(
        no_page="true", for_sync="1", fields="id,code", lookup_field="id", exact_lookups=users[0].pk
    )
    assert response.status_code == 200
    assert response.data == [{"id": users[0].pk, "code": users[0].code}]


def test_normal_pagination_keeps_existing_behavior_for_unserialized_code_field(users):
    response = call_profile_list(fields="id,code", lookup_field="id", exact_lookups=users[0].pk)
    assert response.status_code == 200
    assert response.data == {"count": 1, "results": [{"id": users[0].pk}]}
