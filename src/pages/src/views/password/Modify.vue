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
  <div class="change-password-wrapper">
    <div class="login-box-content">
      <div class="heard-img">
        <img src="../../images/svg/logo_cn.svg" alt="蓝鲸智云" width="160">
      </div>
      <div class="modify-content" data-test-id="passwordInfo">
        <h4 class="common-title">{{$t('更改密码')}}</h4>
        <p class="error-text" v-if="isConfirmError">
          <i class="icon icon-user-exclamation-circle-shape"></i>
          <span class="text">{{errorText}}</span>
        </p>
        <ul>
          <li class="input-list">
            <input type="password"
                   class="select-text"
                   :placeholder="$t('旧密码')"
                   v-model="oldPassword" />
          </li>
          <li class="input-list">
            <input type="password"
                   :class="['select-text', { 'input-error': isConfirmError }]"
                   :placeholder="$t('新密码')"
                   v-model="newPassword"
                   @focus="isConfirmError = false" />
          </li>
          <li class="input-list">
            <input type="password"
                   :class="['select-text', { 'input-error': isConfirmError }]"
                   :placeholder="$t('确认新密码')"
                   v-model="confirmPassword"
                   @focus="isConfirmError = false" />
          </li>
        </ul>
        <bk-button theme="primary"
                   :disabled="!oldPassword || !newPassword || !confirmPassword" class="submit" @click="handlePush">
          {{$t('提交')}}
        </bk-button>
      </div>
    </div>
    <div class="bk-open-set-password">
      <bk-dialog width="440"
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
export default {
  data() {
    return {
      isConfirmError: false,
      errorText: this.$t('两次输入的密码不一致，请重新输入'),
      oldPassword: '',
      newPassword: '',
      confirmPassword: '',
      successDialog: {
        isShow: false,
        title: this.$t('密码修改成功'),
      },
    };
  },
  methods: {
    async handlePush() {
      try {
        if (this.newPassword !== this.confirmPassword) {
          this.isConfirmError = true;
          return;
        }
        const modifyParams = {
          old_password: this.oldPassword,
          new_password: this.confirmPassword.trim(),
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
