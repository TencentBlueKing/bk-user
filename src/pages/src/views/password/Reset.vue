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
  <div class="reset-wrapper">
    <div class="reset-box-content" :class="{ 'before-reset': hasReset === false, 'has-reset': hasReset === true }">
      <div class="login-heard">
        <img src="../../images/svg/logo_cn.svg" alt="蓝鲸智云" width="160">
      </div>
      <div class="login-methond" v-if="!hasReset">
        <bk-radio-group class="fr" v-model="checkMethod">
          <bk-radio-button value="sms">
            {{$t('短信')}}
          </bk-radio-button>
          <bk-radio-button value="email">
            {{$t('邮箱')}}
          </bk-radio-button>
        </bk-radio-group>
      </div>
      <reset-email v-if="checkMethod === 'email'" @has-reset="hasReset = true"></reset-email>
      <reset-sms v-if="checkMethod === 'sms'"></reset-sms>
    </div>
  </div>
</template>

<script>
import ResetEmail from './Email.vue';
import ResetSms from './Sms.vue';

export default {
  name: 'ResetPassword',
  components: {
    'reset-email': ResetEmail,
    'reset-sms': ResetSms,
  },
  data() {
    return {
      checkMethod: 'sms',
      hasReset: false,
    };
  },
};
</script>

<style lang="scss" scoped>
.reset-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #fafbfd;
  z-index: 1000;
}

.reset-box-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: auto;
  width: 400px;
  background: #fff;
  border-radius: 2px;
  box-shadow: 0 0 7px 3px rgba(0, 0, 0, .1);

  &.before-reset {
    max-height: 350px;
  }

  &.has-reset {
    max-height: 326px;
  }
}

.login-heard {
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

.login-methond {
  position: absolute;
  right: 24px;
  top: 120px;
}
</style>
