<!--
  - Tencent is pleased to support the open source community by making Bk-User 蓝鲸用户管理 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for Bk-User 蓝鲸用户管理:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->
<template>
  <div v-if="passportInfo" class="catalog-setting-step local-passport">
    <!-- 基础规则 -->
    <div class="info-container-box">
      <p class="info-container-title">{{$t('基础规则')}}</p>
      <!-- 密码长度 -->
      <div class="info-container">
        <div class="title-container">
          <h4 class="title">{{$t('密码长度')}}</h4>
          <span class="star">*</span>
        </div>
        <bk-input
          v-model="defaultPassword.password_min_length"
          type="number"
          style="width: 240px;"
          :class="{ 'king-input': true, error: passwordLengthError }"
          @input="validatePasswordLength">
          <template slot="append">
            <div class="group-text">{{$t('至32位')}}</div>
          </template>
        </bk-input>
        <p v-show="passwordLengthError" class="error-text">{{$t('密码的长度为8-32位')}}</p>
      </div>

      <!-- 密码必须包含 -->
      <div class="info-container">
        <div class="title-container">
          <h4 class="title">{{$t('密码必须包含')}}</h4>
          <span class="star">*</span>
        </div>
        <bk-checkbox-group v-model="defaultPassword.password_must_includes" style="display: flex;height: 19px;">
          <bk-checkbox value="lower" style="margin-right: 28px;">{{$t('小写字母')}}</bk-checkbox>
          <bk-checkbox value="upper" style="margin-right: 28px;">{{$t('大写字母')}}</bk-checkbox>
          <bk-checkbox value="int" style="margin-right: 28px;">{{$t('数字')}}</bk-checkbox>
          <bk-checkbox value="special" style="margin-right: 28px;">{{$t('特殊字符（除空格）')}}</bk-checkbox>
        </bk-checkbox-group>
        <p class="error-text" v-if="!defaultPassword.password_must_includes.length">{{$t('密码规则不得为空')}}</p>
      </div>

      <!-- 密码不允许 -->
      <div class="info-container">
        <div class="auto-freeze-container">
          <span>{{$t('密码不允许连续')}}</span>
          <bk-input
            v-model="defaultPassword.password_rult_length"
            type="number"
            style="width: 140px;margin: 0 8px;"
            :class="{ 'king-input': true, error: passwordRuleError }"
            @change="handleChange">
            <template slot="append">
              <div class="group-text">{{$t('位')}}</div>
            </template>
          </bk-input>
          <span>{{$t('出现')}}：</span>
        </div>
        <p class="error-text" v-show="passwordRuleError">{{$t('不能小于3位，大于8位')}}</p>
        <bk-checkbox-group
          v-model="defaultPassword.exclude_elements_config"
          style="line-height: 28px;margin-top: 10px;">
          <bk-checkbox value="keyboard_seq" style="margin-right: 28px;">{{$t('键盘序')}}</bk-checkbox>
          <bk-checkbox value="alphabet_seq" style="margin-right: 28px;">{{$t('连续字母序')}}</bk-checkbox>
          <bk-checkbox value="num_seq" style="margin-right: 28px;">{{$t('连续数字序')}}</bk-checkbox>
          <bk-checkbox value="special_seq" style="margin-right: 28px;">{{$t('连续特殊符号序')}}</bk-checkbox>
          <bk-checkbox value="duplicate_char" style="margin-right: 28px;">{{$t('重复字母、数字、特殊符号')}}</bk-checkbox>
        </bk-checkbox-group>
        <p class="error-text" v-show="passwordConfigError">{{$t('密码规则不得为空')}}</p>
      </div>

      <!-- 密码有效期 -->
      <div class="info-container">
        <div class="title-container">
          <h4 class="title">{{$t('密码有效期')}}</h4>
          <span class="star">*</span>
        </div>
        <div class="bk-button-group">
          <bk-button
            v-for="(item, index) in passwordValidDaysList"
            :key="index"
            :class="{ 'is-selected': defaultPassword.password_valid_days === item.days }"
            @click="defaultPassword.password_valid_days = item.days">
            {{item.text}}
          </bk-button>
        </div>
      </div>

      <!-- 密码试错次数 -->
      <div class="info-container">
        <div class="title-container">
          <h4 class="title">{{$t('密码试错次数')}}</h4>
          <span class="star">*</span>
        </div>
        <div class="bk-button-group">
          <bk-button
            v-for="(item, index) in maxTrailTimesList"
            :key="index"
            :class="{ 'is-selected': defaultPassword.max_trail_times === item.times }"
            @click="defaultPassword.max_trail_times = item.times">
            {{item.text}}
          </bk-button>
        </div>
      </div>

      <!-- 密码解锁时间 -->
      <div class="info-container">
        <div class="title-container">
          <h4 class="title">{{$t('自动解锁时间')}}</h4>
          <span class="star">*</span>
          <div class="tips">
            <span class="icon-user--l" v-bk-tooltips="$t('自动解锁时间提示')"></span>
          </div>
        </div>
        <bk-input
          v-model="defaultPassword.auto_unlock_seconds"
          type="number"
          style="width: 240px;"
          :class="{ 'king-input': true, error: autoUnlockError }"
          @input="validateAutoUnlock">
          <template slot="append">
            <div class="group-text">{{$t('秒')}}</div>
          </template>
        </bk-input>
        <p v-show="autoUnlockError" class="error-text">{{$t('自动解锁时间应不少于30秒')}}</p>
      </div>

      <!-- 未登录自动冻结 -->
      <div class="info-container">
        <div class="auto-freeze-container">
          <bk-checkbox v-model="defaultPassword.freeze_after_days.enabled" class="king-checkbox"></bk-checkbox>
          <span>{{$t('连续')}}</span>
          <bk-input
            v-model="defaultPassword.freeze_after_days.value"
            type="number"
            style="width: 120px;margin: 0 8px;"
            :class="{ 'king-input': true, error: freezeDaysError }"
            @input="validateFreezeDays">
            <template slot="append">
              <div class="group-text">{{$t('天')}}</div>
            </template>
          </bk-input>
          <span>{{$t('未登录自动冻结')}}</span>
        </div>
        <p class="error-text" v-if="freezeDaysError">{{$t('请填写正确的登录天数')}}</p>
      </div>
    </div>

    <!-- 初始密码 -->
    <div class="info-container-box" style="margin-top: 40px">
      <p class="info-container-title">{{$t('初始密码')}}</p>
      <!-- 首次登录强制修改密码 -->
      <div class="info-container">
        <bk-checkbox v-model="defaultPassword.force_reset_first_login">{{$t('首次登录强制修改密码')}}</bk-checkbox>
      </div>
      <!-- 密码重复次数设置 -->
      <div class="info-container">
        <div class="change-password">
          <bk-checkbox v-model="defaultPassword.max_password_history.enabled" class="king-checkbox"></bk-checkbox>
          <span>{{$t('修改密码时不能重复前')}}</span>
          <bk-input
            v-model="defaultPassword.max_password_history.value"
            type="number"
            style="width: 120px;margin: 0 8px;"
            :class="{ 'king-input': true, error: passwordHistoryError }"
            @input="validatePasswordHistory">
            <template slot="append">
              <div class="group-text">{{$t('次')}}</div>
            </template>
          </bk-input>
          <span>{{$t('用过的密码')}}</span>
        </div>
        <p v-show="passwordHistoryError" class="error-text">{{$t('不能小于1次')}}</p>
      </div>
      <!-- 初始密码获取方式 -->
      <div class="info-container">
        <div class="title-container">
          <h4 class="title">{{$t('获取方式')}}</h4>
          <span class="star">*</span>
          <div class="tips">
            <span class="icon-user--l" v-bk-tooltips="tipsConfig" ref="tooltipsHtml"></span>
          </div>
          <div id="initialPasswordTips" class="initialPasswordTips">
            <p>
              <span>{{$t('初始密码提示1')}}</span>
            </p>
            <p>
              <span>{{$t('初始密码提示2')}}</span>
              <a :href="mailGateway" target="_blank">{{$t('初始密码提示3')}}</a><span>{{$t('初始密码提示4')}}</span>
            </p>
          </div>
        </div>
        <!-- 邮箱发送随机密码 -->
        <div
          class="init-email-container"
          :class="{ active: defaultPassword.init_password_method === 'random_via_mail',
                    error: initEmailConfigError }">
          <div class="email-config-container" @click="defaultPassword.init_password_method = 'random_via_mail'">
            <bk-radio
              class="king-radio" name="radio1"
              :checked="defaultPassword.init_password_method === 'random_via_mail'">
              {{$t('发送随机密码')}}
            </bk-radio>
          </div>
          <div :class="['tab-password', isEmailTemplate ? 'show-tab-color' : '']">
            <div
              :class="['password-header', defaultPassword.init_password_method !== 'random_via_mail' ? 'hide' : '']">
              <bk-checkbox-group v-model="randomPasswordList">
                <div :class="['password-tab', showEmail ? 'active-tab' : '']" style="margin-left: 5px;">
                  <bk-checkbox
                    value="send_email"
                    :disabled="defaultPassword.init_password_method !== 'random_via_mail'" />
                  <span class="checkbox-item" @click="clickEmail">{{$t('邮箱')}}</span>
                </div>
                <div :class="['password-tab', showSms ? 'active-tab' : '']">
                  <bk-checkbox
                    value="send_sms"
                    :disabled="defaultPassword.init_password_method !== 'random_via_mail'" />
                  <span class="checkbox-item" @click="clickSms">{{$t('短信')}}</span>
                </div>
              </bk-checkbox-group>
              <div class="edit-info" @click="toggleEmailTemplate">
                <span style="font-size:14px">{{$t('编辑通知模板')}}</span>
                <i :class="['bk-icon', isDropdownPassword ? 'icon-angle-up' : 'icon-angle-down']"></i>
              </div>
            </div>
            <div class="password-content">
              <div
                class="template-config-container"
                v-show="showEmail && isEmailTemplate"
                data-test-id="list_emailInfo">
                <ul class="template-config clearfix">
                  <li class="email-block">
                    <h3 class="email-block-name">{{$t('即将到期提醒')}}</h3>
                    <div class="email-info clearfix">
                      <p class="title">{{$t('标题')}}<span class="star">*</span></p>
                      <bk-input
                        type="text" class="input-style" />
                    </div>
                    <div class="email-info clearfix">
                      <p class="title">{{$t('发件人')}}<span class="star">*</span></p>
                      <bk-input
                        type="text" class="input-style" />
                    </div>
                    <div class="email-info clearfix">
                      <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                      <edtiorTemplate
                        :toolbar-config="emailConfig"
                        @updateContent="expiringEmailText" />
                    </div>
                  </li>
                  <li class="email-block">
                    <h3 class="email-block-name">{{$t('已过期提醒')}}</h3>
                    <div class="email-info clearfix">
                      <p class="title">{{$t('标题')}}<span class="star">*</span></p>
                      <bk-input
                        type="text" class="input-style" />
                    </div>
                    <div class="email-info clearfix">
                      <p class="title">{{$t('发件人')}}<span class="star">*</span></p>
                      <bk-input
                        type="text" class="input-style" />
                    </div>
                    <div class="email-info clearfix">
                      <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                      <edtiorTemplate
                        :toolbar-config="emailConfig"
                        @updateContent="expiredEmailText" />
                    </div>
                  </li>
                </ul>
              </div>
              <div
                class="template-config-container"
                v-show="showSms && isEmailTemplate"
                data-test-id="list_emailInfo">
                <ul class="template-config clearfix">
                  <li class="email-block">
                    <h3 class="email-block-name">{{$t('即将到期提醒')}}</h3>
                    <div class="email-info clearfix">
                      <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                      <edtiorTemplate
                        :toolbar-config="infoConfig"
                        @updateContent="expiringSmslText" />
                    </div>
                  </li>
                  <li class="email-block">
                    <h3 class="email-block-name">{{$t('已过期提醒')}}</h3>
                    <div class="email-info clearfix">
                      <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                      <edtiorTemplate
                        :toolbar-config="infoConfig"
                        @updateContent="expiredSmsText" />
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <p class="error-text" v-if="initEmailConfigError">{{$t('请完善模板内容')}}</p>
        <!-- 设置初始密码 -->
        <div
          class="init-password-container"
          :class="{ active: defaultPassword.init_password_method === 'fixed_preset', error: initPasswordError }">
          <div class="king-radio" @click="defaultPassword.init_password_method = 'fixed_preset'">
            <bk-radio
              name="radio1" :checked="defaultPassword.init_password_method === 'fixed_preset'">
              {{$t('统一初始密码')}}
            </bk-radio>
          </div>
          <div class="input-content">
            <input type="text" class="hidden-password-input">
            <input type="password" class="hidden-password-input">
            <input
              class="input-text"
              autocomplete="new-password"
              :type="initPasswordSlash && 'password'"
              :placeholder="$t('请输入密码')"
              :disabled="defaultPassword.init_password_method !== 'fixed_preset'"
              v-model="defaultPassword.init_password"
              @input="validateInitPassword"
            />
            <i :class="['bk-icon', passwordIconClass]" @click="initPasswordSlash = !initPasswordSlash"></i>
          </div>
        </div>
        <p class="error-text" v-show="initPasswordError">{{$t('密码规则校验失败')}}</p>
      </div>
    </div>

    <!-- 密码到期提醒 -->
    <div class="info-container-box" style="margin-top: 40px">
      <p class="info-container-title">{{$t('密码到期提醒')}}</p>
      <!-- 提醒时间 -->
      <div class="info-container">
        <div class="title-container">
          <h4 class="title">{{$t('提醒时间')}}</h4>
          <span class="star">*</span>
          <i class="hint-message icon-user--l" v-bk-tooltips="$t('密码快到期前提醒_如选择_7天__则在密码到期七天前提醒一次')"></i>
        </div>
        <bk-checkbox-group
          style="display: flex;height: 19px;"
          v-model="defaultPassword.password_expiration_notice_interval">
          <bk-checkbox :value="1" style="margin-right: 50px;">{{$t('1天')}}</bk-checkbox>
          <bk-checkbox :value="7" style="margin-right: 50px;">{{$t('7天')}}</bk-checkbox>
          <bk-checkbox :value="15" style="margin-right: 50px;">{{$t('15天')}}</bk-checkbox>
        </bk-checkbox-group>
        <p class="error-text" v-if="passwordDateError">{{$t('账号到期提醒时间不得为空')}}</p>
      </div>

      <!-- 通知方式 -->
      <div class="info-container">
        <div class="title-container">
          <h4 class="title">{{$t('通知方式')}}</h4>
          <span class="star">*</span>
        </div>
        <div :class="['tab-box', isInfoTemplate ? 'show-tab-color' : '']">
          <div class="password-header">
            <bk-checkbox-group v-model="defaultPassword.password_expiration_notice_methods">
              <div :class="['password-tab', showEmail ? 'active-tab' : '']" style="margin-left: 5px;">
                <bk-checkbox value="send_email" />
                <span class="checkbox-item" @click="clickEmail">{{$t('邮箱')}}</span>
              </div>
              <div :class="['password-tab', showSms ? 'active-tab' : '']">
                <bk-checkbox value="send_sms" />
                <span class="checkbox-item" @click="clickSms">{{$t('短信')}}</span>
              </div>
            </bk-checkbox-group>
            <div class="edit-info" @click="toggleInfoTemplate">
              <span style="font-size:14px">{{$t('编辑通知模板')}}</span>
              <i :class="['bk-icon', isDropdownInfo ? 'icon-angle-up' : 'icon-angle-down']"></i>
            </div>
          </div>
          <div class="password-content">
            <div
              class="template-config-container"
              v-show="showEmail && isInfoTemplate"
              data-test-id="list_emailInfo">
              <ul class="template-config clearfix">
                <li class="email-block">
                  <h3 class="email-block-name">{{$t('即将到期提醒')}}</h3>
                  <div class="email-info clearfix">
                    <p class="title">{{$t('标题')}}<span class="star">*</span></p>
                    <bk-input
                      type="text" class="input-style"
                      v-model="expiringEmail.title" />
                  </div>
                  <div class="email-info clearfix">
                    <p class="title">{{$t('发件人')}}<span class="star">*</span></p>
                    <bk-input
                      type="text" class="input-style"
                      v-model="expiringEmail.sender" />
                  </div>
                  <div class="email-info clearfix">
                    <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                    <edtiorTemplate
                      :toolbar-config="emailConfig"
                      :html-text="expiringEmail.content_html"
                      @updateContent="(html, text) => handleEditorText(html, text, 'expiring_password_email_config')" />
                  </div>
                </li>
                <li class="email-block">
                  <h3 class="email-block-name">{{$t('已过期提醒')}}</h3>
                  <div class="email-info clearfix">
                    <p class="title">{{$t('标题')}}<span class="star">*</span></p>
                    <bk-input
                      type="text" class="input-style"
                      v-model="expiredEmail.title" />
                  </div>
                  <div class="email-info clearfix">
                    <p class="title">{{$t('发件人')}}<span class="star">*</span></p>
                    <bk-input
                      type="text" class="input-style"
                      v-model="expiredEmail.sender" />
                  </div>
                  <div class="email-info clearfix">
                    <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                    <edtiorTemplate
                      :toolbar-config="emailConfig"
                      :html-text="expiredEmail.content_html"
                      @updateContent="(html, text) => handleEditorText(html, text, 'expired_password_email_config')" />
                  </div>
                </li>
              </ul>
            </div>
            <div
              class="template-config-container"
              v-show="showSms && isInfoTemplate"
              data-test-id="list_emailInfo">
              <ul class="template-config clearfix">
                <li class="email-block">
                  <h3 class="email-block-name">{{$t('即将到期提醒')}}</h3>
                  <div class="email-info clearfix">
                    <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                    <edtiorTemplate
                      :toolbar-config="infoConfig"
                      :html-text="expiringSms.content_html"
                      @updateContent="(html, text) => handleEditorText(html, text, 'expiring_password_sms_config')" />
                  </div>
                </li>
                <li class="email-block">
                  <h3 class="email-block-name">{{$t('已过期提醒')}}</h3>
                  <div class="email-info clearfix">
                    <p class="title" style="height: 260px">{{$t('正文')}}<span class="star">*</span></p>
                    <edtiorTemplate
                      :toolbar-config="infoConfig"
                      :html-text="expiredSms.content_html"
                      @updateContent="(html, text) => handleEditorText(html, text, 'expired_password_sms_config')" />
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div class="info-container">
        <bk-checkbox>{{$t('从未登录蓝鲸平台的用户_不发送密码到期提醒通知')}}</bk-checkbox>
      </div>
    </div>

    <!-- 新增用户目录 -->
    <div v-if="type === 'add'" class="save-setting-buttons">
      <bk-button @click="$emit('cancel')" class="king-button">
        {{$t('返回列表')}}
      </bk-button>
      <bk-button @click="$emit('previous')" class="king-button">
        {{$t('上一步')}}
      </bk-button>
      <bk-button theme="primary" @click="pushInfo" class="king-button" :disabled="isDisabledSubmit">
        {{$t('提交')}}
      </bk-button>
    </div>

    <!-- 编辑用户目录设置 -->
    <div v-if="type === 'set'" class="save-setting-buttons">
      <bk-button theme="primary" @click="saveInfo" class="king-button" :disabled="isDisabledSubmit">
        {{$t('保存')}}
      </bk-button>
      <bk-button @click="$emit('cancel')" class="king-button">
        {{$t('取消')}}
      </bk-button>
    </div>
  </div>
</template>

<script>
import edtiorTemplate from '../operation/editorTemplate.vue';

export default {
  components: { edtiorTemplate },
  props: {
    // add 添加用户目录 set 设置密码相关
    type: {
      type: String,
      default: '',
    },
    passportInfo: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      mailGateway: window.BK_MAIL_GATEWAY,
      tipsConfig: {
        allowHtml: true,
        content: '#initialPasswordTips',
      },
      // 密码长度是否错误
      passwordLengthError: false,
      passwordHistoryError: false,
      // 密码不允许连续出现
      passwordRuleError: false,
      passwordConfigError: false,
      // 密码解锁时间是否错误
      autoUnlockError: false,
      // 未登录自动冻结天数是否错误
      freezeDaysError: false,
      // 设置初始密码规则校验是否错误
      initPasswordError: false,
      // 邮箱发送随机密码模板设置是否错误
      initEmailConfigError: false,

      // 初始密码是否以星号展示
      initPasswordSlash: true,
      // 密码试错次数
      maxTrailTimesList: [{
        times: 3,
        text: `3${this.$t('次')}`,
      }, {
        times: 5,
        text: `5${this.$t('次')}`,
      }, {
        times: 10,
        text: `10${this.$t('次')}`,
      }],
      showEmail: true,
      showSms: false,
      // 显示获取方式编辑模板
      isEmailTemplate: false,
      // 显示通知方式编辑模板
      isInfoTemplate: false,
      randomPasswordList: ['send_email', 'send_sms'],
      isDropdownPassword: false,
      isDropdownInfo: false,
      /* 邮箱工具栏配置 */
      emailConfig: {
        toolbarKeys: [
          'bold', 'italic', 'color',
          {
            key: 'group-justify',
            iconSvg: `<svg viewBox="0 0 1024 1024">
              <path d="M768 793.6v102.4H51.2v-102.4h716.8z m204.8-230.4v102.4H51.2v-102.4h921.6z
                m-204.8-230.4v102.4H51.2v-102.4h716.8zM972.8 102.4v102.4H51.2V102.4h921.6z"></path>
            </svg>`,
            menuKeys: ['justifyLeft', 'justifyRight', 'justifyCenter', 'justifyJustify'],
          },
          'insertLink',
        ],
      },
      /* 短信工具栏配置 */
      infoConfig: {
        toolbarKeys: ['insertLink'],
      },
      passwordDateError: false,
    };
  },
  computed: {
    // 密码有效期
    passwordValidDaysList() {
      return this.$store.state.passwordValidDaysList;
    },
    // default region
    defaultPassword() {
      return this.passportInfo ? this.passportInfo : null;
    },
    // 密码输入框右边的眼睛 icon
    passwordIconClass() {
      return this.initPasswordSlash ? 'icon-eye-slash' : 'icon-eye';
    },
    isDisabledSubmit() {
      return !this.defaultPassword.password_must_includes.length
                    || this.passwordLengthError
                    || this.passwordHistoryError
                    || this.passwordRuleError
                    || this.passwordConfigError
                    || this.autoUnlockError
                    || this.freezeDaysError
                    || this.initPasswordError
                    || this.initEmailConfigError
                    || this.passwordDateError;
    },
    expiredEmail() {
      return this.passportInfo.expired_password_email_config || {};
    },
    expiringEmail() {
      return this.passportInfo.expiring_password_email_config || {};
    },
    expiringSms() {
      return this.passportInfo.expiring_password_sms_config || {};
    },
    expiredSms() {
      return this.passportInfo.expired_password_sms_config || {};
    },
  },
  watch: {
    passportInfo() {
      this.init();
    },
    'defaultPassword.exclude_elements_config'(newVal) {
      if (newVal.length) {
        this.validatePasswordRule();
        this.passwordConfigError = false;
      } else if (!newVal.length && this.defaultPassword.password_rult_length) {
        this.passwordConfigError = true;
      } else {
        this.passwordRuleError = false;
        this.passwordConfigError = false;
      }
    },
    'defaultPassword.password_expiration_notice_methods'(val) {
      if (val.length && !this.defaultPassword.password_expiration_notice_interval.length) {
        this.passwordDateError = true;
      } else {
        this.passwordDateError = false;
      }
    },
    'defaultPassword.password_expiration_notice_interval'(val) {
      if (!val.length && this.defaultPassword.password_expiration_notice_methods.length) {
        this.passwordDateError = true;
      } else {
        this.passwordDateError = false;
      }
    },
  },
  created() {
    if (this.passportInfo) {
      this.init();
    }
  },
  methods: {
    handleChange(value) {
      if (value !== '') {
        this.validatePasswordRule();
        if (!this.defaultPassword.exclude_elements_config.length) {
          this.passwordConfigError = true;
        }
      } else if (this.defaultPassword.exclude_elements_config.length) {
        this.passwordRuleError = true;
        this.passwordConfigError = false;
      } else {
        this.passwordRuleError = false;
        this.passwordConfigError = false;
      }
    },
    init() {
      // 监听密码规则的变化去验证初始密码
      this.$watch(() => {
        return this.passportInfo.password_must_includes.length;
      }, () => {
        this.validateInitPassword();
      });
    },
    // 校验密码长度
    validatePasswordLength() {
      this.passwordLengthError = this.defaultPassword.password_min_length < 8
                                 || this.defaultPassword.password_min_length > 32;
    },
    validatePasswordRule() {
      this.passwordRuleError = this.defaultPassword.password_rult_length < 3
                                 || this.defaultPassword.password_rult_length > 8;
    },
    // 校验密码重复次数
    validatePasswordHistory() {
      this.passwordHistoryError = this.defaultPassword.max_password_history.value <= 0;
    },
    // 校验密码解锁时间
    validateAutoUnlock() {
      this.autoUnlockError = this.defaultPassword.auto_unlock_seconds < 30;
    },
    // 校验未登录自动冻结天数
    validateFreezeDays() {
      this.freezeDaysError = this.defaultPassword.freeze_after_days.value <= 0;
    },
    // 验证初始密码是否符合密码规则
    validateInitPassword() {
      const password = this.defaultPassword.init_password;
      const passwordRules = {
        passwordMinLength: this.defaultPassword.password_min_length,
        passwordMustIncludes: this.defaultPassword.password_must_includes,
      };
      this.initPasswordError = !this.$validatePassportByRules(password, passwordRules);
    },
    // 验证邮箱模板
    validateEmailTemplate() {
      const contentList = [...Object.values(this.defaultPassword.init_mail_config),
        ...Object.values(this.defaultPassword.reset_mail_config)];
      for (let i = 0; i < contentList.length; i++) {
        if (!contentList[i].length) {
          this.initEmailConfigError = true;
          return;
        }
      }
      this.initEmailConfigError = false;
    },
    // 提交前验证是否有错误
    validate() {
      this.validatePasswordLength();
      this.validateAutoUnlock();
      this.validateFreezeDays();
      this.validateInitPassword();
      this.validateEmailTemplate();
      const error = this.passwordLengthError
                    || this.autoUnlockError
                    || this.freezeDaysError
                    || this.initPasswordError
                    || this.initEmailConfigError;
      return !error;
    },
    // 提交
    pushInfo() {
      this.validate() && this.$emit('pushPassword');
    },
    // 保存
    saveInfo() {
      this.validate() && this.$emit('savePassport');
    },
    // 展开或隐藏邮件模板
    toggleEmailTemplate() {
      if (this.defaultPassword.init_password_method === 'random_via_mail') {
        this.isDropdownPassword = !this.isDropdownPassword;
        this.isEmailTemplate = !this.isEmailTemplate;
      }
    },
    toggleInfoTemplate() {
      this.isDropdownInfo = !this.isDropdownInfo;
      this.isInfoTemplate = !this.isInfoTemplate;
    },
    clickEmail() {
      this.showEmail = true;
      this.showSms = false;
    },
    clickSms() {
      this.showEmail = false;
      this.showSms = true;
    },
    handleEditorText(html, text, key) {
      this.defaultPassword[key].content_html = html;
      this.defaultPassword[key].content = text;
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../../scss/mixins/scroller';

.initialPasswordTips {
  p {
    padding: 4px 0;
  }

  a {
    color: #699df4;
  }
}

#catalog .catalog-setting-step.local-passport .info-container-box {
  > .info-container-title {
    font-size: 14px;
    font-family: MicrosoftYaHei, MicrosoftYaHei-Bold;
    font-weight: 700;
    color: #63656e;
    padding-bottom: 10px;
    border-bottom: 1px solid #dcdee5;
  }
  > .info-container {
    margin: 17px 0;
    // 设置初始密码
    > .init-password-container {
      position: relative;
      width: 860px;
      height: 42px;
      line-height: 42px;
      color: #63656e;
      font-size: 0;
      border: 1px solid #c4c6cc;
      border-radius: 2px;
      margin-top: 9px;
      display: flex;
      align-items: center;
      &:hover {
        border: 1px solid #A3C5FD;
      }

      &.active {
        border: 1px solid #699df4;
        .input-content {
          color: #63656e;
          .input-text, .bk-icon {
            cursor: pointer;
          }
        }
      }

      &.error {
        border: 1px solid #ea3636;
      }

      > .king-radio,
      .input-text {
        display: inline-block;
        vertical-align: middle;
        font-size: 14px;
        cursor: pointer;
        width: 90%;
      }

      > .king-radio {
        cursor: pointer;
        padding: 0 38px 0 25px;
        width: 20%;
      }
      .input-content {
        display: flex;
        width: 80%;
        color: #DCDEE5;
        > .input-text {
          line-height: 19px;
          width: 70%;
          border: none;
          resize: none;
          outline: none;
          cursor: not-allowed;
          &::input-placeholder {
            color: #c3cdd7;
          }
        }

        > .bk-icon {
          position: absolute;
          right: 12px;
          top: 11px;
          font-size: 18px;
          cursor: not-allowed;
          width: 10%;
        }
      }
    }
    // 发送随机密码
    > .init-email-container {
      width: 860px;
      border: 1px solid #c4c6cc;
      border-radius: 2px;
      cursor: pointer;
      &:hover {
        border: 1px solid #A3C5FD;
      }

      &.active {
        border: 1px solid #699df4;

        > .email-config-container > .edit-template {
          color: #3a84ff;
        }
      }

      &.error {
        border: 1px solid #ea3636;
      }

      > .email-config-container {
        position: relative;
        font-size: 0;
        color: #63656e;
        line-height: 42px;
        height: 42px;
        border: none;

        > .king-radio {
          display: inline-block;
          vertical-align: middle;
          font-size: 14px;
          cursor: pointer;
          padding: 0 38px 0 25px;
        }

        > .edit-template {
          position: absolute;
          right: 14px;
          top: 11px;
          line-height: 19px;
          font-size: 14px;
          color: #c4c6cc;

          &.disable {
            cursor: not-allowed;
          }
        }
      }
    }

    > .auto-freeze-container, .change-password {
      display: flex;
      align-items: center;
      font-size: 14px;

      > .king-checkbox {
        padding: 0;
        margin-right: 8px;
      }
    }
    .edit-template {
      font-size: 14px;
      color: #3a84ff;
      &:hover {
        cursor: pointer;
      }
    }

    .template-config-container {
      position: relative;
      width: 100%;

      > ul.template-config > li.email-block {
        width: 50%;
        float: left;

        &:first-child {
          border-right: 1px solid #dcdee5;
        }

        > .email-block-name {
          height: 42px;
          line-height: 42px;
          text-align: center;
          font-size: 14px;
          font-weight: bold;
          background: #fafbfd;
        }

        > .email-info {
          font-size: 0;
          border-top: 1px solid #dcdee5;
          display: flex;

          input,
          textarea {
            resize: none;
            outline: none;
            border: none;
          }

          .title,
          .input-text,
          .textarea-text {
            font-size: 14px;
          }

          .title {
            padding: 13px 0 10px 0;
            width: 20%;
            // float: left;
            text-align: center;
            border-right: 1px solid #dcdee5;

            .star {
              display: inline-block;
              vertical-align: middle;
              margin: 0 0 0 3px;
              line-height: 19px;
              color: #ff5e5e;
            }
          }

          .input-text {
            width: 80%;
            padding: 13px 0 10px 19px;
          }

          ::v-deep .input-style {
            width: 80%;
            .bk-input-text .bk-form-input {
              height: 44px;
              border: 1px solid #fff;
            }
          }

          .focus-editor {
            border: 1px solid #3c96ff;
          }

          ::v-deep .textarea-text {
            width: 80%;
            height: 260px;
            line-height: 20px;
            font-size: 14px;
            font-weight: 400;
            word-break: break-all;
            background: #fff;
            overflow: hidden;
            overflow-y: auto;

            @include scroller($backgroundColor: #e6e9ea, $width: 4px);

            .bk-textarea-wrapper {
              height: 100%;
              border: none;
              .bk-form-textarea {
                height: 100%;
                &::-webkit-scrollbar {
                  width: 4px;
                  background-color: transparent;
                }
                &::-webkit-scrollbar-thumb {
                  border-radius: 4px;
                  background-color: #dcdee5;
                }
              }
            }
          }

          ::v-deep .bk-form-control.control-active .bk-textarea-wrapper {
            border: 1px solid #3A84FF;
          }

          ::v-deep .markdown-box {
            width: 80%;
            height: 260px;
            line-height: 20px;
            font-size: 14px;
            font-weight: 400;
            word-break: break-all;
            background: #fff;
            overflow: hidden;
            .toolbar-content {
              height: 40px;
              .w-e-toolbar {
                background-color: #F0F2F5;
                padding-left: 15px;
              }
            }
            .editor-content {
              width: 100%;
              height: calc(100% - 40px);
              overflow-y: auto;
              @include scroller($backgroundColor: #e6e9ea, $width: 4px);
              .w-e-text-container .w-e-scroll {
                overflow: inherit !important;
              }
            }
          }
        }
      }
    }
    ::v-deep .tab-box {
      border: 1px solid #3A84FF;
    }

    ::v-deep .tab-box, .tab-password {
      width: 860px;
      .password-header {
        display: flex;
        line-height: 50px;
        .bk-form-control {
          display: flex;
          width: 85%;
          .password-tab {
            padding-left: 20px;
            .checkbox-item {
              font-size: 14px;
              display: inline-block;
              padding: 0 20px 0 5px;
            }
          }
        }
        .edit-info {
          color: #3A84FF;
          :hover {
            cursor: pointer;
          }
        }
      }
      .hide {
        cursor: not-allowed;
        .edit-info {
          color: #DCDEE5;
          :hover {
            cursor: not-allowed;
          }
        }
      }
    }
    ::v-deep .show-tab-color {
      .password-header {
        display: flex;
        border-bottom: 1px solid #dcdee5;
        .active-tab {
          border-bottom: 2px solid #3A84FF;
        }
        .password-tab span:hover {
          cursor: pointer;
          color: #3a84ff;
        }
      }
      .password-content {
        padding: 20px;
        .template-config-container {
          border: 1px solid #dcdee5;
        }
      }
      .bk-tab-label-list .bk-tab-label-item.active:after {
        height: 2px;
      }
      .bk-tab-header {
        background-image: linear-gradient(transparent 41px, #dcdee5 0);
      }
    }
  }
}
</style>
