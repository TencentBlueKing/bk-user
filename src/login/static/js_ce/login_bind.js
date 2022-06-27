/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function refresh_token(){
    var csrftoken = getCookie('bklogin_csrftoken');
    $('input[name="csrfmiddlewaretoken"]').val(csrftoken);
    return true;
}


$(document).ready(function(){
    // 点击查看协议
    $('.action .protocol-btn').click(function(event) {
        $('.protocol-pop').show();
    });

    // 关闭协议弹窗
    $('.protocol-pop .close').click(function(event) {
        $('.protocol-pop').hide();
    });

    $('.consent-content .consent-btn').click(function(){
        $('.protocol-pop').hide();
    });


    // 判断当前的浏览器是谷歌 及证书验证过期
    $('#close-chrome').click(function() {
        $('.is-chrome').hide();
    })
    var isChrome = navigator.userAgent.toLowerCase().match(/chrome/) != null;
    if (!isChrome) {
        $('.is-chrome').show();
    } else {
        $('.is-chrome').hide();
    }

    $('#code-btn').click(function() {
        if ($('#code-btn').html() !== '验证码') {
            getCode();
        }
    })
});

function getCode() {
    // 获取验证码
    var btn = $('#code-btn');
    var code = $('#validation');
    var count = 60;
    var timer = setInterval(() => {
        if (count > 1) {
            count --;
            btn.attr('class', 'code-btn-hide');
            btn.html('验证码');
            code.attr('placeholder', `获取验证码（${count}s）`);
        } else {
            clearInterval(timer);
            btn.html('获取验证码');
            btn.attr('class', 'code-btn');
            code.attr('placeholder', '');
        }
    }, 1000);
}

window.onload = function() {
    this.getCode();
}
