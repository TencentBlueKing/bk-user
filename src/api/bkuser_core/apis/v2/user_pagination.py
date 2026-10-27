"""供两个 v2 用户列表接口复用的限量、去重分页器。"""

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.core.paginator import InvalidPage, Paginator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from bkuser_core.apis.v2.viewset import StandardResultsSetPagination
from bkuser_core.common.error_codes import error_codes
from bkuser_global.utils import force_str_2_bool


class _UserCountPaginator(Paginator):
    @cached_property
    def count(self):
        # COUNT 只需要匹配后的唯一用户主键，不应把 extras、logo 等大字段带入去重子查询。
        return self.object_list.order_by().values("pk").count()


class UserResultsPagination(StandardResultsSetPagination):
    django_paginator_class = _UserCountPaginator

    @staticmethod
    def _positive_setting(name):
        try:
            value = getattr(settings, name)
        except AttributeError:
            raise ImproperlyConfigured(f"必须配置 {name}")
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ImproperlyConfigured(f"{name} 必须是正整数")
        return value

    def get_page_size(self, request):
        self.max_page_size = self._positive_setting("MAX_PAGE_SIZE")
        # 沿用 DRF 及旧接口行为：非法值回落到默认页大小，超过上限的值自动收敛到配置上限。
        return super().get_page_size(request)

    @staticmethod
    def _query_params_error(message):
        """使用项目统一业务错误，避免企业版响应暴露 DRF 的 ErrorDetail 表示。"""
        return error_codes.QUERY_PARAMS_ERROR.format(message=message, replace=True)

    @staticmethod
    def _prepare_queryset(queryset):
        """在 COUNT/LIMIT 前按用户去重，并保证用户之间的排序唯一、稳定。"""
        query = queryset.query
        ordering = query.extra_order_by or query.order_by
        if not ordering and query.default_ordering:
            ordering = queryset.model._meta.ordering
        ordering = list(ordering or ["pk"])
        for item in ordering:
            if not isinstance(item, str) or item == "?":
                raise UserResultsPagination._query_params_error(_("ordering 不支持随机排序或排序表达式"))
            name = item.lstrip("-")
            if name in query.extra_select or name in query.annotations:
                continue
            model = queryset.model
            for part in name.split("__"):
                try:
                    field = model._meta.pk if part == "pk" else model._meta.get_field(part)
                except FieldDoesNotExist:
                    raise UserResultsPagination._query_params_error(_("ordering 请使用用户自身字段"))
                if field.many_to_many or field.one_to_many:
                    raise UserResultsPagination._query_params_error(
                        _("ordering 不支持多值部门或上级关系字段，请使用 id 等用户自身字段")
                    )
                model = field.related_model if field.is_relation else None
                if model is None:
                    break

        pk_names = {"pk", queryset.model._meta.pk.name, queryset.model._meta.pk.attname}
        if not any(item.lstrip("-") in pk_names for item in ordering):
            ordering.append("pk")
        queryset = queryset.order_by(*ordering)

        # 部门、上级、登录记录等多值关系 JOIN 会放大用户行；prefetch 不会。
        # 仅在确实存在多值 JOIN 时增加 DISTINCT，避免无关联查询承担无意义的去重成本。
        if any(
            getattr(getattr(join, "join_field", None), "one_to_many", False)
            or getattr(getattr(join, "join_field", None), "many_to_many", False)
            for join in queryset.query.alias_map.values()
        ):
            queryset = queryset.distinct()
        return queryset

    def _can_defer(self, queryset, offset):
        if not getattr(settings, "ENABLE_DEFERRED_PAGINATION", False):
            return False
        threshold = self._positive_setting("DEFERRED_PAGINATION_MIN_OFFSET")
        query = queryset.query
        pk_names = {"pk", queryset.model._meta.pk.name, queryset.model._meta.pk.attname}
        ordering = query.order_by
        return (
            offset >= threshold
            and len(ordering) == 1
            and ordering[0].lstrip("-") in pk_names
            and not query.extra_order_by
            and not query.group_by
            and not query.annotations
            and not query.combinator
            and not query.select_for_update
        )

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.unpaginated = force_str_2_bool(request.query_params.get("no_page", False))
        queryset = self._prepare_queryset(queryset)

        if self.unpaginated:
            limit = self._positive_setting("USER_LIST_NO_PAGE_LIMIT")
            # 先只探测“上限 + 1”个唯一主键；确认未超限后才加载用户资料及其关系数据。
            ids = list(
                queryset.select_related(None)
                .prefetch_related(None)
                .order_by("pk")
                .values_list("pk", flat=True)[: limit + 1]
            )
            if len(ids) > limit:
                raise self._query_params_error(
                    _(
                        "匹配用户超过 %(limit)s 人，no_page 不支持返回该结果集；"
                        "请去掉 no_page，从 page=1 开始使用 page/page_size 分页，"
                        "并根据响应中的 count 计算总页数"
                    )
                    % {"limit": limit}
                )
            # 正式取数继续保留原过滤条件，并限定为探测到的主键，避免并发新增绕过 no_page 上限。
            return list(queryset.filter(pk__in=ids)) if ids else []

        page_size = self.get_page_size(request)
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)
        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            raise NotFound(self.invalid_page_message.format(page_number=page_number, message=str(exc)))
        self.display_page_controls = paginator.num_pages > 1 and self.template is not None
        offset = (self.page.number - 1) * page_size
        if not self._can_defer(queryset, offset):
            return list(self.page)

        page_ids = list(
            queryset.select_related(None)
            .prefetch_related(None)
            .values_list("pk", flat=True)[offset : offset + page_size]
        )
        objects = {obj.pk: obj for obj in queryset.filter(pk__in=page_ids)}
        if len(page_ids) != len(objects):
            # 两段 SQL 之间可能有用户离开结果集；此时按当前数据重新执行一次普通 OFFSET 分页。
            # 只回退一次，不递归重试，避免持续写入时形成无休止查询。
            return super().paginate_queryset(queryset, request, view)
        rows = [objects[pk] for pk in page_ids]
        self.page.object_list = rows
        return rows

    def get_paginated_response(self, data):
        if self.unpaginated:
            return Response(data)
        return super().get_paginated_response(data)
