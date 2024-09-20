<template>
  <div class="reset-wrapper">
    <div class="reset-box-content">
      <template v-if="!showEmailSend">
        <div class="reset-password-header">
          <p class="title">{{ $t('忘记密码') }}</p>
          <p class="subtitle">{{ tipsText }}</p>
        </div>
        <div class="reset-password-tab">
          <div
            class="tab-item"
            v-for="item in resetPasswordMethod"
            :key="item.value"
            @click="handleChangeMethod(item.value)">
            <span :class="activeMethod === item.value ? 'active' : ''">
              {{ item.label }}
            </span>
          </div>
          <Phone v-if="activeMethod === 'phone'" :tenant-id="tenantId" />
          <Email v-if="activeMethod === 'email'" :tenant-id="tenantId" @email-send="emailSend" />
        </div>
      </template>
      <template v-else>
        <EmailSent :current-email="currentEmail" @email-send="emailSend" />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import Email from './emailForm.vue';
import EmailSent from './emailSent.vue';
import Phone from './phoneForm.vue';

import { t } from '@/language/index';

const route = useRoute();

const tenantId = ref('');
const activeMethod = ref('phone');

watch(() => route.query.tenantId, (id: string) => {
  if (id) {
    tenantId.value = id;
  }
}, {
  immediate: true,
});

const tipsText = computed(() => (activeMethod.value === 'phone'
  ? t('请输入手机号以接收短信验证码')
  : t('请输入邮箱以接收邮件重置密码链接')));
const resetPasswordMethod = ref([
  {
    label: t('手机号'),
    value: 'phone',
  },
  {
    label: t('邮箱'),
    value: 'email',
  },
]);

const handleChangeMethod = (method: string) => {
  activeMethod.value = method;
};

const showEmailSend = ref(false);
const currentEmail = ref('');
const emailSend = (status: boolean, email: string) => {
  showEmailSend.value = status;
  currentEmail.value = email;
};
</script>

<style lang="less" scoped>
.reset-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 999;
  width: 100%;
  height: 100%;
  background: #fafbfd;
}

.reset-box-content {
  position: absolute;
  inset: 0;
  width: 480px;
  height: 474px;
  padding: 40px 40px 32px;
  margin: auto;
  background: #FFF;
  border-radius: 10px;
  box-shadow: 0 4px 12px 0 #0003;

  .reset-password-header {
    color: #313238;

    .title {
      height: 42px;
      margin-bottom: 32px;
      font-size: 32px;
      font-weight: 700;
    }

    .subtitle {
      margin-bottom: 24px;
      font-size: 20px;
      line-height: 28px;
      color: #313238;
    }
  }

  .reset-password-tab {
    width: 400px;
    margin-bottom: 24px;
    font-size: 14px;
    line-height: 22px;
    color: #63656E;
    white-space: nowrap;

    .tab-item {
      display: inline-block;
      width: 200px;
      margin-bottom: 34px;
      text-align: center;
      cursor: pointer;

      span {
        padding-bottom: 10px;

        &.active {
          font-size: 16px;
          font-weight: 700;
          color: #3A84FF;
          border-bottom: 2px solid #3A84FF;
        }
      }
    }
  }
}

</style>

