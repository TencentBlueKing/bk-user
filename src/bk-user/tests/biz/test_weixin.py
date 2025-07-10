# -*- coding: utf-8 -*-
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

import hashlib
import time
from unittest import mock

import pytest
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.weixin import WeixinBindHandler, WeixinConfigService, WeixinUtil
from bkuser.utils.std_error import APIError
from django.test import RequestFactory

pytestmark = pytest.mark.django_db


class TestWeixinUtil:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_store_and_get_qrcode_user_info(self, random_tenant):
        tenant_user = TenantUser.objects.first()
        ticket = "test_ticket_123"

        # 存储用户信息
        WeixinUtil.store_qrcode_user_info(ticket, tenant_user.id)

        # 获取用户信息
        retrieved_user = WeixinUtil.get_tenant_user_by_ticket(ticket)
        assert retrieved_user.id == tenant_user.id

        # 验证缓存已被删除
        with pytest.raises(APIError) as error:
            WeixinUtil.get_tenant_user_by_ticket(ticket)
        assert "微信二维码 ticket 无效或已过期" in str(error.value.message)

    def test_get_tenant_user_by_invalid_ticket(self):
        with pytest.raises(APIError) as error:
            WeixinUtil.get_tenant_user_by_ticket("invalid_ticket")
        assert "微信二维码 ticket 无效或已过期" in str(error.value.message)

    def test_xml_to_dict_success(self):
        xml_data = """<xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[fromUser]]></FromUserName>
            <CreateTime>1348831860</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[this is a test]]></Content>
            <MsgId>1234567890123456</MsgId>
        </xml>"""

        result = WeixinUtil.xml_to_dict(xml_data)
        expected = {
            "ToUserName": "toUser",
            "FromUserName": "fromUser",
            "CreateTime": "1348831860",
            "MsgType": "text",
            "Content": "this is a test",
            "MsgId": "1234567890123456",
        }
        assert result == expected

    def test_xml_to_dict_invalid_xml(self):
        invalid_xml = "<xml><invalid>"

        with pytest.raises(APIError) as error:
            WeixinUtil.xml_to_dict(invalid_xml)
        assert "XML 解析失败" in error.value.message


class TestWeixinBindHandler:
    @pytest.fixture
    def mock_request(self):
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}
        return request

    @pytest.fixture
    def mock_tenant_user(self, _init_tenant_users_depts, random_tenant):
        return TenantUser.objects.first()

    @pytest.fixture
    def weixin_handler(self, mock_tenant_user, mock_request):
        with mock.patch.object(WeixinConfigService, "get_weixin_settings") as mock_get_weixin_settings:
            mock_get_weixin_settings.return_value = {
                "wx_type": "qy",
                "corp_id": "test_corp_id",
                "agent_id": "test_agent_id",
            }
            return WeixinBindHandler(mock_tenant_user, mock_request)

    def test_tenant_id_property(self, weixin_handler, mock_tenant_user):
        assert weixin_handler.tenant_id == mock_tenant_user.tenant_id

    def test_state_session_key_property(self, weixin_handler, mock_tenant_user):
        expected_key = f"wecom_bind_state_{mock_tenant_user.id}"
        assert weixin_handler.state_session_key == expected_key

    @mock.patch.object(WeixinConfigService, "get_weixin_settings", return_value={"wx_type": "qy"})
    @mock.patch.object(
        WeixinBindHandler, "_get_wecom_bind_info", return_value={"bind_type": "wecom", "bind_url": "test_url"}
    )
    def test_get_bind_info_wecom(
        self, mock_get_wecom_bind_info, mock_get_weixin_settings, weixin_handler, mock_request
    ):
        result = weixin_handler.get_bind_info()

        assert result["bind_type"] == "wecom"
        assert result["bind_url"] == "test_url"

    @mock.patch.object(WeixinConfigService, "get_weixin_settings", return_value={"wx_type": "mp"})
    @mock.patch.object(
        WeixinBindHandler, "_get_mp_bind_info", return_value={"bind_type": "mp", "bind_url": "test_url"}
    )
    def test_get_bind_info_mp(self, mock_get_mp_bind_info, mock_get_weixin_settings, weixin_handler, mock_request):
        result = weixin_handler.get_bind_info()

        assert result["bind_type"] == "mp"
        assert result["bind_url"] == "test_url"

    def test_generate_and_store_state(self, weixin_handler, mock_request):
        state = weixin_handler._generate_and_store_state()

        # 验证 state 不为空
        assert state
        assert len(state) > 0

        # 验证 session 中存储了数据
        session_key = weixin_handler.state_session_key
        state_data = mock_request.session.get(session_key)
        assert state_data is not None
        assert state_data["state"] == state
        assert state_data["tenant_user_id"] == weixin_handler.tenant_user.id

    def test_check_state_valid(self, weixin_handler, mock_request):
        # 生成并存储 state
        state = weixin_handler._generate_and_store_state()

        # 检查 state
        result = weixin_handler.check_state(state)
        assert result is True

        # 验证 session 已被清理
        session_key = weixin_handler.state_session_key
        assert session_key not in mock_request.session

    def test_check_state_invalid(self, weixin_handler, mock_request):
        result = weixin_handler.check_state("invalid_state")
        assert result is False

    def test_check_state_expired(self, weixin_handler, mock_request):
        # 生成并存储 state
        state = weixin_handler._generate_and_store_state()

        # 模拟时间过期
        session_key = weixin_handler.state_session_key
        state_data = mock_request.session[session_key]
        state_data["timestamp"] = int(time.time()) - 301  # 超过 300 秒
        mock_request.session[session_key] = state_data

        result = weixin_handler.check_state(state)
        assert result is False

    def test_bind_user(self, weixin_handler, mock_tenant_user):
        """测试绑定用户"""
        wx_userid = "test_wx_userid"

        weixin_handler.bind_user(wx_userid)

        # 验证用户已被绑定
        mock_tenant_user.refresh_from_db()
        assert mock_tenant_user.wx_userid == wx_userid

    @mock.patch("bkuser.biz.weixin.http_get", return_value=(True, {"errcode": 0, "userid": "test_userid"}))
    @mock.patch.object(WeixinConfigService, "get_access_token", return_value="test_access_token")
    def test_get_wecom_userid_success(self, mock_get_access_token, mock_http_get, weixin_handler):
        """测试成功获取企业微信用户 ID"""
        result = weixin_handler.get_wecom_userid("test_code")
        assert result == "test_userid"

    @mock.patch("bkuser.biz.weixin.http_get", return_value=(False, {"error": "network error"}))
    @mock.patch.object(WeixinConfigService, "get_access_token", return_value="test_access_token")
    def test_get_wecom_userid_api_error(self, mock_get_access_token, mock_http_get, weixin_handler):
        """测试企业微信 API 错误"""
        with pytest.raises(APIError) as error:
            weixin_handler.get_wecom_userid("test_code")
        assert "获取企业微信用户信息失败" in str(error.value.message)

    @mock.patch("bkuser.biz.weixin.http_get", return_value=(True, {"errcode": 40013, "errmsg": "invalid appid"}))
    @mock.patch.object(WeixinConfigService, "get_access_token", return_value="test_access_token")
    def test_get_wecom_userid_errcode_error(self, mock_get_access_token, mock_http_get, weixin_handler):
        with pytest.raises(APIError) as error:
            weixin_handler.get_wecom_userid("test_code")
        assert "企业微信 API 调用失败" in str(error.value.message)

    @mock.patch.object(WeixinBindHandler, "bind_user")
    def test_handle_qrcode_event_subscribe(self, mock_bind_user, weixin_handler):
        event_data = {
            "MsgType": "event",
            "Event": "subscribe",
            "FromUserName": "test_from_user",
            "ToUserName": "test_to_user",
        }

        result = weixin_handler.handle_qrcode_event(event_data)

        # 验证绑定被调用
        mock_bind_user.assert_called_once_with("test_from_user")

        # 验证返回的 XML 包含正确内容
        assert "test_to_user" in result
        assert "test_from_user" in result
        assert "绑定成功" in result

    @mock.patch.object(WeixinBindHandler, "bind_user")
    def test_handle_qrcode_event_scan(self, mock_bind_user, weixin_handler):
        event_data = {
            "MsgType": "event",
            "Event": "SCAN",
            "FromUserName": "test_from_user",
            "ToUserName": "test_to_user",
        }

        result = weixin_handler.handle_qrcode_event(event_data)

        # 验证绑定被调用
        mock_bind_user.assert_called_once_with("test_from_user")

        # 验证返回的 XML 包含正确内容
        assert "test_to_user" in result
        assert "test_from_user" in result
        assert "绑定成功" in result

    def test_handle_qrcode_event_invalid_event(self, weixin_handler):
        event_data = {
            "MsgType": "event",
            "Event": "unsubscribe",
            "FromUserName": "test_from_user",
            "ToUserName": "test_to_user",
        }

        result = weixin_handler.handle_qrcode_event(event_data)
        assert result == ""

    def test_handle_qrcode_event_missing_data(self, weixin_handler):
        event_data = {
            "MsgType": "event",
            "Event": "subscribe",
            # 缺少 FromUserName 和 ToUserName
        }

        result = weixin_handler.handle_qrcode_event(event_data)
        assert result == ""

    @mock.patch("bkuser.biz.weixin.http_post", return_value=(True, {"errcode": 0, "ticket": "test_ticket"}))
    @mock.patch.object(WeixinConfigService, "get_access_token", return_value="test_access_token")
    @mock.patch.object(WeixinUtil, "store_qrcode_user_info")
    def test_get_mp_qrcode_url_success(
        self, mock_store_qrcode_user_info, mock_get_access_token, mock_http_post, weixin_handler
    ):
        result = weixin_handler._get_mp_qrcode_url()

        # 验证存储被调用
        mock_store_qrcode_user_info.assert_called_once_with("test_ticket", weixin_handler.tenant_user.id)

        # 验证返回的 URL
        assert "test_ticket" in result
        assert "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=" in result

    @mock.patch("bkuser.biz.weixin.http_post", return_value=(False, {"error": "network error"}))
    @mock.patch.object(WeixinConfigService, "get_access_token", return_value="test_access_token")
    def test_get_mp_qrcode_url_api_error(self, mock_get_access_token, mock_http_post, weixin_handler):
        """测试微信公众号 API 错误"""
        with pytest.raises(APIError) as error:
            weixin_handler._get_mp_qrcode_url()
        assert "创建微信临时二维码失败" in str(error.value.message)

    @mock.patch("bkuser.biz.weixin.http_post", return_value=(True, {"errcode": 40013, "errmsg": "invalid appid"}))
    @mock.patch.object(WeixinConfigService, "get_access_token", return_value="test_access_token")
    def test_get_mp_qrcode_url_errcode_error(self, mock_get_access_token, mock_http_post, weixin_handler):
        """测试微信公众号返回错误码"""
        with pytest.raises(APIError) as error:
            weixin_handler._get_mp_qrcode_url()
        assert "微信公众号 API 调用失败" in error.value.message


class TestWeixinConfigService:
    """测试微信配置服务"""

    @pytest.fixture
    def weixin_config_service(self, random_tenant):
        return WeixinConfigService(random_tenant.id)

    @mock.patch.object(
        WeixinConfigService, "get_weixin_settings", return_value={"wx_type": "qy", "corp_id": "test_corp_id"}
    )
    def test_get_weixin_settings(self, mock_get_weixin_settings, weixin_config_service):
        result = weixin_config_service.get_weixin_settings()

        assert result["wx_type"] == "qy"
        assert result["corp_id"] == "test_corp_id"

    @mock.patch.object(WeixinConfigService, "get_access_token", return_value="test_access_token")
    def test_get_access_token(self, mock_get_access_token, weixin_config_service):
        result = weixin_config_service.get_access_token()
        assert result == "test_access_token"

    @mock.patch.object(WeixinConfigService, "get_weixin_settings", return_value={"wx_token": "test_token"})
    def test_check_sign_valid(self, mock_get_weixin_settings, weixin_config_service):
        token = "test_token"
        timestamp = "1234567890"
        nonce = "test_nonce"

        # 计算正确的签名
        params = [token, timestamp, nonce]
        params.sort()
        s = "".join(params)
        correct_signature = hashlib.sha1(s.encode("utf-8")).hexdigest()

        result = weixin_config_service.check_sign(correct_signature, timestamp, nonce)
        assert result is True

    @mock.patch.object(WeixinConfigService, "get_weixin_settings", return_value={"wx_token": "test_token"})
    def test_check_sign_invalid(self, mock_get_weixin_settings, weixin_config_service):
        timestamp = "1234567890"
        nonce = "test_nonce"
        invalid_signature = "invalid_signature"

        result = weixin_config_service.check_sign(invalid_signature, timestamp, nonce)
        assert result is False

    @mock.patch.object(WeixinConfigService, "get_weixin_settings", return_value={})
    def test_check_sign_no_token(self, mock_get_weixin_settings, weixin_config_service):
        result = weixin_config_service.check_sign("signature", "timestamp", "nonce")
        assert result is False
