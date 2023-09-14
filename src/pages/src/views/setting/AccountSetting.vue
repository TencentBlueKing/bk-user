<template>
  <bk-loading :loading="isLoading" :z-index="9" class="account-setting-wrapper user-scroll-y">
    <bk-form class="account-setting-content" form-type="vertical">
      <bk-form-item label="账号有效期开启">
        <bk-switcher v-model="state.accountValidOpen" theme="primary" size="large" />
      </bk-form-item>
      <div v-if="state.accountValidOpen">
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
        <bk-form-item label="通知方式" property="config.notification.enabled_methods" required>
          <NotifyEditorTemplate
            v-if="formData.config.notification"
            :active-methods="activeMethods"
            :checkbox-info="checkboxInfo"
            :data-list="formData.config.notification.templates"
            :is-template="isAccountExpire"
            :expiring-email-key="'password_expiring'"
            :expired-email-key="'password_expired'"
            :expiring-sms-key="'password_expiring'"
            :expired-sms-key="'password_expired'"
            @handleEditorText="handleEditorText">
            <template #label>
              <div class="password-header">
                <bk-checkbox-group
                  class="checkbox-zh"
                  v-model="formData.config.notification.enabled_methods"
                  @change="handleChange">
                  <bk-checkbox
                    v-for="(item, index) in checkboxInfo" :key="index"
                    :class="['password-tab', item.status ? 'active-tab' : '']"
                    style="margin-left: 5px;"
                    :label="item.value">
                    <span class="checkbox-item" @click="handleClickLabel(item)">{{item.label}}</span>
                  </bk-checkbox>
                </bk-checkbox-group>
                <div class="edit-info" @click="accountExpireTemplate">
                  <span style="font-size:14px">编辑通知模板</span>
                  <AngleUp v-if="isDropdownAccountExpire" />
                  <AngleDown v-else />
                </div>
              </div>
            </template>
          </NotifyEditorTemplate>
        </bk-form-item>
      </div>
    </bk-form>
    <div class="account-setting-footer">
      <bk-button theme="primary" class="mr8">应用</bk-button>
      <bk-button>重置</bk-button>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { AngleDown, AngleUp } from 'bkui-vue/lib/icon';
import { onMounted, reactive, ref } from 'vue';

import NotifyEditorTemplate from '@/components/notify-editor/NotifyEditorTemplate.vue';
import { getDefaultConfig } from '@/http/dataSourceFiles';

const isLoading = ref(false);
const formData = reactive({
  config: {},
});
const activeMethods = ref('email');
const isAccountExpire = ref(false);
const isDropdownAccountExpire = ref(false);

const checkboxInfo = [
  { value: 'email', label: '邮箱', status: true },
  { value: 'sms', label: '短信', status: false },
];

onMounted(async () => {
  isLoading.value = true;
  const res = await getDefaultConfig('local');
  formData.config = res?.data?.config?.password_expire;
  isLoading.value = false;
});

const handleEditorText = (html, text, key, type) => {
  formData.config.notification.templates.forEach((item) => {
    if (item.method === type && item.scene === key) {
      item.content = text;
      item.content_html = html;
    }
  });
};


const handleClickLabel = (item) => {
  checkboxInfo.forEach((element) => {
    element.status = element.value === item.value;
  });
};

const accountExpireTemplate = () => {
  isAccountExpire.value = !isAccountExpire.value;
  isDropdownAccountExpire.value = !isDropdownAccountExpire.value;
};

const handleChange = () => {
  window.changeInput = true;
};

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
@import url('@/components/notify-editor/NotifyEditor.less');

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
