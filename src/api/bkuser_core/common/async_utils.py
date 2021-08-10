# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import asyncio as aio

from asgiref.sync import sync_to_async
from rest_framework import status
from rest_framework.response import Response


class AsyncMixin:
    """Provides async view compatible support for DRF Views and ViewSets.

    This must be the first inherited class.

        class MyViewSet(AsyncMixin, GenericViewSet):
            pass
    """

    @classmethod
    def as_view(cls, *args, **initkwargs):
        """Make Django process the view as an async view."""
        view = super().as_view(*args, **initkwargs)

        async def async_view(*args, **kwargs):
            # wait for the `dispatch` method
            return await view(*args, **kwargs)

        async_view.csrf_exempt = True
        return async_view

    async def dispatch(self, request, *args, **kwargs):
        """Add async support."""
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers

        try:
            await sync_to_async(self.initial)(request, *args, **kwargs)  # MODIFIED HERE

            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            # accept both async and sync handlers
            # built-in handlers are sync handlers
            if not aio.iscoroutinefunction(handler):  # MODIFIED HERE
                handler = sync_to_async(handler)  # MODIFIED HERE
            response = await handler(request, *args, **kwargs)  # MODIFIED HERE

        except Exception as exc:  # pylint: disable=broad-except
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response


class AsyncCreateModelMixin:
    """Make `create()` and `perform_create()` overridable.

    Without inheriting this class, the event loop can't be used in these two methods when override them.

    This must be inherited before `CreateModelMixin`.

        class MyViewSet(AsyncMixin, GenericViewSet, AsyncCreateModelMixin, CreateModelMixin):
            pass
    """

    async def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)  # MODIFIED HERE
        await self.perform_create(serializer)  # MODIFIED HERE
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    async def perform_create(self, serializer):
        await sync_to_async(serializer.save)()


class AsyncDestroyModelMixin:
    """Make `destroy()` and `perform_destroy()` overridable.

    Without inheriting this class, the event loop can't be used in these two methods when override them.

    This must be inherited before `DestroyModelMixin`.

        class MyViewSet(AsyncMixin, GenericViewSet, AsyncDestroyModelMixin, DestroyModelMixin):
            pass
    """

    async def destroy(self, request, *args, **kwargs):
        instance = await sync_to_async(self.get_object)()  # MODIFIED HERE
        await self.perform_destroy(instance)  # MODIFIED HERE
        return Response(status=status.HTTP_204_NO_CONTENT)

    async def perform_destroy(self, instance):
        await sync_to_async(instance.delete)()  # MODIFIED HERE


# other mixins can be created similarly
