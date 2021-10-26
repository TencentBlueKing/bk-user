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
    <!-- 密码长度 -->
    <div class="info-container">
      <div class="title-container">
        <h4 class="title">{{$t('密码长度')}}</h4>
        <span class="star">*</span>
      </div>
      <bk-input v-model="defaultPassword.password_min_length"
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

    <!-- 密码有效期 -->
    <div class="info-container">
      <div class="title-container">
        <h4 class="title">{{$t('密码有效期')}}</h4>
        <span class="star">*</span>
      </div>
      <div class="bk-button-group">
        <bk-button v-for="(item, index) in passwordValidDaysList"
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
        <bk-button v-for="(item, index) in maxTrailTimesList"
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
      <bk-input v-model="defaultPassword.auto_unlock_seconds"
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

    <!-- 初始密码获取方式 -->
    <div class="info-container">
      <div class="title-container">
        <h4 class="title">{{$t('初始密码获取方式')}}</h4>
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
      <!-- 设置初始密码 -->
      <div class="init-password-container"
           :class="{ active: defaultPassword.init_password_method === 'fixed_preset', error: initPasswordError }"
           @click="defaultPassword.init_password_method = 'fixed_preset'">
        <bk-radio name="radio1" :checked="defaultPassword.init_password_method === 'fixed_preset'" class="king-radio">
          {{$t('统一初始密码')}}
        </bk-radio>
        <input type="text" class="hidden-password-input">
        <input type="password" class="hidden-password-input">
        <input class="input-text"
               autocomplete="new-password"
               :type="initPasswordSlash && 'password'"
               :placeholder="$t('请输入密码')"
               v-model="defaultPassword.init_password"
               @input="validateInitPassword"
        />
        <i :class="['bk-icon', passwordIconClass]" @click="initPasswordSlash = !initPasswordSlash"></i>
      </div>
      <p class="error-text" v-show="initPasswordError">{{$t('密码规则校验失败')}}</p>
      <!-- 邮箱发送随机密码 -->
      <div class="init-email-container" :class="{ active: defaultPassword.init_password_method === 'random_via_mail',
                                                  error: initEmailConfigError }">
        <div class="email-config-container" @click="defaultPassword.init_password_method = 'random_via_mail'">
          <bk-radio class="king-radio" name="radio1"
                    :checked="defaultPassword.init_password_method === 'random_via_mail'">
            {{$t('邮箱发送随机密码')}}
          </bk-radio>
          <span class="edit-template" :class="{ disable: defaultPassword.init_password_method === 'fixed_preset' }"
                @click.stop="toggleEmailTemplate">
            {{$t('编辑邮件模板')}}
          </span>
        </div>
        <div class="template-config-container" v-show="showEmailTemplate" data-test-id="list_emailInfo">
          <i class="arrow"></i>
          <ul class="template-config clearfix">
            <li class="email-block">
              <h3 class="email-block-name">{{$t('创建账户邮件')}}</h3>
              <div class="email-info clearfix">
                <p class="title">{{$t('标题')}}<span class="star">*</span></p>
                <input type="text" class="input-text" v-model="defaultPassword.init_mail_config.title"
                       @input="validateEmailTemplate" />
              </div>
              <div class="email-info clearfix">
                <p class="title">{{$t('发件人')}}<span class="star">*</span></p>
                <input type="text" class="input-text" v-model="defaultPassword.init_mail_config.sender"
                       @input="validateEmailTemplate" />
              </div>
              <div class="email-info clearfix">
                <p class="title" style="height: 191px">{{$t('正文')}}<span class="star">*</span></p>
                <textarea class="textarea-text" v-model="defaultPassword.init_mail_config.content"
                          @input="validateEmailTemplate"></textarea>
              </div>
            </li>
            <li class="email-block">
              <h3 class="email-block-name">{{$t('重设密码后的邮件')}}</h3>
              <div class="email-info clearfix">
                <p class="title">{{$t('标题')}}<span class="star">*</span></p>
                <input type="text" class="input-text" v-model="defaultPassword.reset_mail_config.title"
                       @input="validateEmailTemplate" />
              </div>
              <div class="email-info clearfix">
                <p class="title">{{$t('发件人')}}<span class="star">*</span></p>
                <input type="text" class="input-text" v-model="defaultPassword.reset_mail_config.sender"
                       @input="validateEmailTemplate" />
              </div>
              <div class="email-info clearfix">
                <p class="title" style="height: 191px">{{$t('正文')}}<span class="star">*</span></p>
                <textarea class="textarea-text" v-model="defaultPassword.reset_mail_config.content"
                          @input="validateEmailTemplate"></textarea>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <p class="error-text" v-if="initEmailConfigError">{{$t('请完善模板内容')}}</p>
    </div>

    <!--        <div class="info-container">-->
    <!--            <bk-checkbox v-model="defaultPassword.force_reset_first_login">{{$t('首次登录强制修改密码')}}</bk-checkbox>-->
    <!--        </div>-->

    <!-- 未登录自动冻结 -->
    <div class="info-container">
      <div class="auto-freeze-container">
        <bk-checkbox v-model="defaultPassword.enable_auto_freeze" class="king-checkbox"></bk-checkbox>
        <span>{{$t('连续')}}</span>
        <bk-input v-model="defaultPassword.freeze_after_days"
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
export default {
  components: {},
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
      // 编辑邮件模板
      showEmailTemplate: false,
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
    };
  },
  computed: {
    // 密码有效期
    passwordValidDaysList() {
      return this.$store.state.passwordValidDaysList;
    },
    // default region
    defaultPassword() {
      return this.passportInfo ? this.passportInfo.default : null;
    },
    // 密码输入框右边的眼睛 icon
    passwordIconClass() {
      return this.initPasswordSlash ? 'icon-eye-slash' : 'icon-eye';
    },
    isDisabledSubmit() {
      return !this.defaultPassword.password_must_includes.length
                    || this.passwordLengthError
                    || this.autoUnlockError
                    || this.freezeDaysError
                    || this.initPasswordError
                    || this.initEmailConfigError;
    },
  },
  watch: {
    passportInfo() {
      this.init();
    },
  },
  created() {
    if (this.passportInfo) {
      this.init();
    }
  },
  methods: {
    init() {
      // 监听密码规则的变化去验证初始密码
      this.$watch(() => {
        return this.passportInfo.default.password_must_includes.length;
      }, () => {
        this.validateInitPassword();
      });
    },
    // 校验密码长度
    validatePasswordLength() {
      this.passwordLengthError = this.defaultPassword.password_min_length < 8
                                 || this.defaultPassword.password_min_length > 32;
    },
    // 校验密码解锁时间
    validateAutoUnlock() {
      this.autoUnlockError = this.defaultPassword.auto_unlock_seconds < 30;
    },
    // 校验未登录自动冻结天数
    validateFreezeDays() {
      this.freezeDaysError = this.defaultPassword.freeze_after_days <= 0;
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
        this.showEmailTemplate = !this.showEmailTemplate;
      }
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

#catalog .catalog-setting-step.local-passport {
  > .info-container {
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

      &.active {
        border: 1px solid #699df4;
      }

      &.error {
        border: 1px solid #ea3636;
      }

      > .king-radio,
      .input-text {
        display: inline-block;
        vertical-align: middle;
        font-size: 14px;
      }

      > .king-radio {
        cursor: pointer;
        padding: 0 38px 0 8px;
      }

      > .input-text {
        line-height: 19px;
        width: 70%;
        border: none;
        resize: none;
        outline: none;

        &::input-placeholder {
          color: #c3cdd7;
        }
      }

      > .bk-icon {
        position: absolute;
        right: 12px;
        top: 11px;
        font-size: 18px;
        cursor: pointer;
      }
    }
    // 邮箱发送随机密码
    > .init-email-container {
      margin-top: 9px;
      width: 860px;
      border: 1px solid #c4c6cc;
      border-radius: 2px;
      cursor: pointer;

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
          padding: 0 38px 0 8px;
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

      > .template-config-container {
        position: relative;
        width: 100%;
        border-top: 1px solid #c4c6cc;

        > .arrow {
          position: absolute;
          top: -6px;
          right: 50px;
          width: 10px;
          height: 10px;
          border-top: 1px solid #dcdee5;
          border-left: 1px solid #dcdee5;
          background: #fafbfd;
          transform: rotate(45deg);
          z-index: 10;
        }

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
              float: left;
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

            .textarea-text {
              padding: 12px 20px 0 20px;
              width: 80%;
              height: 191px;
              line-height: 20px;
              font-size: 14px;
              font-weight: 400;
              word-break: break-all;
              background: #fff;
              overflow: hidden;
              overflow-y: auto;

              @include scroller($backgroundColor: #e6e9ea, $width: 4px);
            }
          }
        }
      }
    }

    > .auto-freeze-container {
      display: flex;
      align-items: center;
      font-size: 14px;

      > .king-checkbox {
        padding: 0;
        margin-right: 8px;
      }
    }
  }
}
</style>
