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
  <div class="login-content">
    <div class="reset-pw">
      <div class="reset-content" v-if="hasReset === false">
        <h4 class="common-title">{{$t('重置密码')}}</h4>
        <p :class="['text', { 'show-error-info': isError }]">{{$t('请输入账户绑定的邮箱，我们将为您发送密码重置邮件')}}</p>
        <p class="error-text" v-if="isError">
          <i class="icon icon-user-exclamation-circle-shape"></i>
          <span class="text">{{$t('邮箱格式错误，请重新输入')}}</span>
        </p>
        <input
          type="text"
          :class="['select-text', { 'input-error': isError }]"
          :placeholder="$t('请输入邮箱')"
          v-model="resetEmail"
          @focus="hiddenError" />
        <bk-button
          theme="primary"
          class="submit"
          :disabled="!resetEmail"
          @click="submitEmailPw">
          {{$t('发送密码重置邮件')}}
        </bk-button>
      </div>
    </div>
    <div class="reset-content" v-if="hasReset === true">
      <h4 class="common-title">{{$t('已发送密码重置邮件')}}</h4>
      <p class="text" style="margin: 0 0 18px 0">{{$t('已发送至您的邮箱')}}：{{resetEmail}}<br />{{$t('请查看邮件并根据提示进行操作')}}</p>
      <bk-button theme="primary" class="submit" @click="goEmail">{{$t('前往邮箱')}}</bk-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResetEmail',
  data() {
    return {
      isError: false,
      resetEmail: '',
      hasReset: false,
    };
  },
  methods: {
    hiddenError() {
      this.isError = false;
    },
    async submitEmailPw() {
      try {
        // eslint-disable-next-line no-useless-escape
        const reEmail = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
        if (!reEmail.test(this.resetEmail)) {
          this.isError = true;
          return;
        }
        // 调用接口
        const emailParams = { email: this.resetEmail };
        await this.$store.dispatch('password/reset', emailParams);
        this.hasReset = true;
        this.$emit('has-reset', true);
      } catch (e) {
        console.warn(e);
      }
    },
    goEmail() {
      const emailUrl = this.resetEmail.split('@')[1];
      window.open(`https://mail.${emailUrl}`);
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
