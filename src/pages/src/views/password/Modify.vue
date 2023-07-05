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
  <div class="change-password-wrapper">
    <div class="login-box-content">
      <div class="heard-img">
        <img v-if="$i18n.locale === 'zh-cn'" src="../../images/svg/logo_cn.svg" alt="蓝鲸智云" width="160">
        <img v-else src="../../images/logo_en.png" :alt="$t('蓝鲸智云')" width="160">
      </div>
      <div class="modify-content" data-test-id="passwordInfo">
        <h4 class="common-title">{{$t('更改密码')}}</h4>
        <p class="error-text" v-if="isConfirmError || isCorrectPw">
          <i class="icon icon-user-exclamation-circle-shape"></i>
          <span class="text">{{errorText}}</span>
        </p>
        <ul>
          <li class="input-list">
            <input
              type="password"
              class="select-text"
              :placeholder="$t('旧密码')"
              v-model="oldPassword" />
          </li>
          <li class="input-list">
            <input
              type="password"
              :class="['select-text', { 'input-error': isConfirmError || isCorrectPw }]"
              :placeholder="$t('新密码')"
              v-model="newPassword"
              @focus="handleFocus" />
          </li>
          <li class="input-list">
            <input
              type="password"
              :class="['select-text', { 'input-error': isConfirmError || isCorrectPw }]"
              :placeholder="$t('确认新密码')"
              v-model="confirmPassword"
              @focus="handleFocus" />
          </li>
        </ul>
        <bk-button
          theme="primary"
          :disabled="!oldPassword || !newPassword || !confirmPassword" class="submit" @click="handlePush">
          {{$t('提交')}}
        </bk-button>
      </div>
    </div>
    <div class="bk-open-set-password">
      <bk-dialog
        width="440"
        header-position="left"
        v-model="successDialog.isShow"
        :title="successDialog.title"
        @confirm="register">
        <div style="min-height: 20px;">
          <p class="text" style="margin: 0 0 18px 0">{{$t('点击确定后将跳到蓝鲸登录页面')}}</p>
        </div>
      </bk-dialog>
    </div>
  </div>
</template>

<script>
const Base64 = require('js-base64').Base64;
export default {
  name: 'ModifyBox',
  data() {
    return {
      isConfirmError: false,
      errorText: '',
      oldPassword: '',
      newPassword: '',
      confirmPassword: '',
      successDialog: {
        isShow: false,
        title: this.$t('密码修改成功'),
      },
      // 公钥
      publicKey: '',
      // 是否rsa加密
      isRsaEncrypted: false,
      passwordRules: {
        passwordMinLength: 0,
        passwordMustIncludes: [],
      },
      isCorrectPw: false,
    };
  },
  mounted() {
    this.initRsa();
  },
  methods: {
    async initRsa() {
      try {
        const res = await this.$store.dispatch('password/getRsa', this.$route.query.token || '');
        if (res.data) {
          res.data.forEach((item) => {
            switch (item.key) {
              case 'enable_password_rsa_encrypted':
                return this.isRsaEncrypted = item.value;
              case 'password_rsa_public_key':
                return this.publicKey = Base64.decode(item.value);
              case 'password_min_length':
                return this.passwordRules.passwordMinLength = item.value;
              case 'password_must_includes':
                return this.passwordRules.passwordMustIncludes = item.value;
            }
          });
        }
      } catch (e) {
        console.warn(e);
      }
    },
    async handlePush() {
      try {
        // 确认密码是否一致
        if (this.newPassword !== this.confirmPassword) {
          this.isConfirmError = true;
          this.errorText = this.$t('两次输入的密码不一致，请重新输入');
          return;
        }
        // 校验密码规则
        this.isCorrectPw = !this.$validatePassportByRules(this.newPassword, this.passwordRules);
        if (this.isCorrectPw) {
          this.errorText = this.$getMessageByRules(this, this.passwordRules);
          return;
        }
        if (this.isRsaEncrypted) {
          this.oldPassword = Base64.encode(this.Rsa.rsaPublicData(this.oldPassword.trim(), this.publicKey));
          this.newPassword = Base64.encode(this.Rsa.rsaPublicData(this.newPassword.trim(), this.publicKey));
          this.confirmPassword = Base64.encode(this.Rsa.rsaPublicData(this.confirmPassword.trim(), this.publicKey));
        } else {
          this.oldPassword = Base64.encode(this.oldPassword.trim());
          this.newPassword = Base64.encode(this.newPassword.trim());
          this.confirmPassword = Base64.encode(this.confirmPassword.trim());
        }
        const modifyParams = {
          old_password: this.oldPassword,
          new_password: this.confirmPassword,
        };
        await this.$store.dispatch('password/modify', modifyParams);
        this.successDialog.isShow = true;
      } catch (e) {
        console.warn(e);
      }
    },
    register() {
      window.location.href = window.login_url;
    },
    handleFocus() {
      this.isError = false;
      this.isCorrectPw = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.change-password-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #fafbfd;
  z-index: 1000;

  .login-box-content {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    margin: auto;
    width: 400px;
    max-height: 410px;
    background: #fff;
    border-radius: 2px;
    box-shadow: 0 0 7px 3px rgba(0, 0, 0, .1);
  }

  .modify-content {
    padding: 0 24px;
    font-size: 14px;
  }

  .heard-img {
    width: 400px;
    height: 100px;
    line-height: 100px;
    text-align: center;
    background: #192948;
    border-radius: 2px 2px 0 0;

    img {
      vertical-align: middle;
    }
  }

  .input-list {
    margin-bottom: 20px;
  }

  .common-title {
    margin: 10px 0;
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

  .error-text {
    margin-bottom: 10px;
    color: #ea3636;
    font-size: 14px;

    .icon {
      color: #ea3636;
    }
  }
}
</style>
