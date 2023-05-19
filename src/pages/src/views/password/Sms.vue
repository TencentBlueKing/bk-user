<!--
  - TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
  - Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
  - Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at http://opensource.org/licenses/MIT
  - Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
  - an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
  - specific language governing permissions and limitations under the License.
  -->
<template>
  <div class="login-content">
    <div class="reset-pw">
      <div class="reset-content">
        <h4 class="common-title">{{$t('重置密码')}}</h4>
        <template v-if="step === 'sendSms'">
          <p :class="['text', { 'show-error-info': isError }]">{{$t('请输入账号信息，我们将为您发送重置密码短信')}}</p>
          <p class="error-text" v-if="isError">
            <i class="icon icon-user-exclamation-circle-shape"></i>
            <span class="text">{{errorMessage}}</span>
          </p>
          <input
            type="text"
            :class="['select-text', { 'input-error': isError }]"
            :placeholder="$t('请输入用户名/手机号')"
            v-model="telephone"
            @focus="hiddenError" />
          <bk-button
            theme="primary"
            class="submit"
            :disabled="!telephone"
            @click="sendSms">
            {{$t('发送验证码')}}
          </bk-button>
        </template>
        <template v-if="step === 'sendCode'">
          <p :class="['text', { 'show-error-info': isError }]">{{$t('已向')}}{{simplePhone}}{{ $t('发送验证码') }}</p>
          <p class="error-text" v-if="isError">
            <i class="icon icon-user-exclamation-circle-shape"></i>
            <span class="text">{{errorMessage}}</span>
          </p>
          <div class="code-wrapper">
            <input
              type="text"
              style="width: 200px;"
              class="fl"
              :class="['select-text', { 'input-error': isError }]"
              :placeholder="$t('请输入验证码')"
              v-model="verificationCode"
              @focus="hiddenError" />
            <bk-button
              theme="primary"
              style="width: 140px;"
              class="fr"
              :disabled="remainTime > 0"
              @click="sendSms">
              <template v-if="remainTime > 0">
                {{remainTime}}{{$t('后')}}
              </template>
              {{$t('重新发送')}}
            </bk-button>
          </div>
          <bk-button
            theme="primary"
            class="submit"
            :disabled="!verificationCode"
            @click="sendCode">
            {{$t('提交')}}
          </bk-button>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResetTelephone',
  data() {
    return {
      isError: false,
      telephone: '',
      simplePhone: '',
      verificationCode: '',
      verificationCodeToken: '',
      step: 'sendSms',
      hasReset: false,
      remainTime: 0,
      timer: 0,
      errorMessage: '',
    };
  },
  beforeDestory() {
    clearInterval(this.timer);
  },
  methods: {
    hiddenError() {
      this.isError = false;
    },
    async sendSms() {
      try {
        const telephoneParams = { telephone: this.telephone };
        const { result, message, data } = await this.$store.dispatch('password/sendSms', telephoneParams);
        if (result) {
          this.step = 'sendCode';
          this.simplePhone = data.telephone;
          this.verificationCodeToken = data.verification_code_token;
          this.remainTime = 60; // 1分钟
          // 验证码倒计时
          clearInterval(this.timer);
          this.timer = setInterval(() => {
            this.remainTime = this.remainTime - 1;
          }, 1000);
          this.$bkMessage({
            theme: 'success',
            message: this.$t('发送成功'),
          });
        } else {
          this.showErrorMessage(message);
        }
      } catch (e) {
        console.warn(e);
      }
    },
    async sendCode() {
      try {
        const codeParams = {
          verification_code_token: this.verificationCodeToken,
          verification_code: this.verificationCode,
        };
        const { result, message, data } = await this.$store.dispatch('password/sendCode', codeParams);
        if (result) {
          this.$router.push({
            name: 'setPassword',
            query: {
              token: data.token,
            },
          });
        } else {
          this.showErrorMessage(message);
        }
      } catch (e) {
        console.warn(e);
      }
    },
    showErrorMessage(message) {
      this.errorMessage = message;
      this.isError = true;
    },
  },
};
</script>

<style lang="scss" scoped>
.login-content {
  padding: 0 24px;
  font-size: 14px;
}

.common-title {
  margin: 20px 0 15px 0;
  font-size: 20px;
  font-weight: 400;
  color: rgba(49, 50, 56, 1);
  line-height: 28px;
}

.select-text {
  padding-left: 12px;

  &::input-placeholder {
    color: rgba(195, 205, 215, 1);
  }
}

.submit {
  width: 100%;
}
// 重置密码
.reset-content {
  .text {
    font-size: 14px;
    font-weight: 400;
    color: rgba(99, 101, 110, 1);
    line-height: 20px;
    margin: 10px 0 20px;

    &.show-error-info {
      margin-bottom: 10px;
    }
  }

  .select-text {
    margin-bottom: 20px;
  }
}
// 错误提示
.error-text {
  margin-bottom: 10px;
  color: #ea3636;
  font-size: 14px;

  .text {
    color: #ea3636;
  }

  .icon {
    color: #ea3636;
  }
}
</style>
