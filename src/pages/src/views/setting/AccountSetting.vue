<template>
  <div class="account-setting-wrapper user-scroll-y">
    <bk-form class="account-setting-content" form-type="vertical">
      <bk-form-item label="账号有效期开启">
        <bk-switcher v-model="state.accountValidOpen" theme="primary" size="large" />
      </bk-form-item>
      <bk-form-item label="账号有效期">
        <bk-radio-group v-model="state.accountValidDays">
          <bk-radio-button
            v-for="(item, index) in accountCof.accountValidDays"
            :key="index"
            :label="item.days"
          >
            {{ item.text }}
          </bk-radio-button>
        </bk-radio-group>
      </bk-form-item>
      <bk-form-item label="提醒时间" required>
        <bk-checkbox-group v-model="state.accountExpirationNoticeInterval">
          <bk-checkbox
            v-for="(item, index) in accountCof.accountExpirationNoticeInterval"
            :key="index"
            :label="item.value"
          >{{ item.label }}</bk-checkbox
          >
        </bk-checkbox-group>
      </bk-form-item>
    </bk-form>
    <div class="account-setting-footer">
      <bk-button theme="primary" class="mr8">应用</bk-button>
      <bk-button>重置</bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue';

const state = reactive({
  accountValidOpen: true,
  accountValidDays: 30,
  accountExpirationNoticeInterval: [1, 7],
  accountExpirationNoticeMethods: ['email', 'SMS'],
});

const accountCof = reactive({
  accountValidDays: [
    { days: 30, text: '一个月' },
    { days: 90, text: '三个月' },
    { days: 180, text: '六个月' },
    { days: 365, text: '一年' },
    { days: -1, text: '永久' },
  ],
  accountExpirationNoticeInterval: [
    { value: 1, label: '1天' },
    { value: 7, label: '7天' },
    { value: 15, label: '15天' },
  ],
});
</script>

<style lang="less" scoped>
.account-setting-wrapper {
  padding: 24px;

  .account-setting-content {
    padding: 24px 40px;
    background: #fff;
    border-radius: 2px;
    box-shadow: 0 2px 4px 0 #1919290d;

    :deep(.bk-form-item) {
      &:last-child {
        margin-bottom: 0;
      }
    }
  }

  .account-setting-footer {
    margin-top: 16px;

    button {
      width: 88px;
    }
  }
}
</style>
