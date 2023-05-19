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
  <div class="reset-wrapper">
    <div class="reset-box-content" :class="{ 'before-reset': hasReset === false, 'has-reset': hasReset === true }">
      <div class="login-heard">
        <img v-if="$i18n.locale === 'zh-cn'" src="../../images/svg/logo_cn.svg" alt="蓝鲸智云" width="160">
        <img v-else src="../../images/logo_en.png" :alt="$t('蓝鲸智云')" width="160">
      </div>
      <div class="login-methond" v-if="!hasReset">
        <bk-radio-group class="fr" v-model="checkMethod">
          <bk-radio-button value="sms">
            {{ $t('短信') }}
          </bk-radio-button>
          <bk-radio-button value="email">
            {{ $t('邮箱') }}
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
