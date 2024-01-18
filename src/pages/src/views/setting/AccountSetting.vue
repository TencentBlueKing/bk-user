<template>
  <bk-loading :loading="isLoading" :z-index="9" class="account-setting-wrapper user-scroll-y">
    <bk-form class="account-setting-content" form-type="vertical" :model="formData" ref="formRef">
      <bk-form-item :label="$t('账号有效期开启')">
        <bk-switcher v-model="formData.enabled" theme="primary" size="large" @change="changeEnabled" />
      </bk-form-item>
      <div v-if="formData.enabled">
        <bk-form-item :label="$t('账号有效期')" required>
          <bk-radio-group v-model="formData.validity_period" @change="handleChange">
            <bk-radio-button
              v-for="(item, index) in VALID_TIME"
              :key="index"
              :label="item.days"
            >
              {{ item.text }}
            </bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item :label="$t('续期提醒时间')" property="remind_before_expire" required>
          <bk-checkbox-group v-model="formData.remind_before_expire" @change="handleChange">
            <bk-checkbox
              v-for="(item, index) in REMIND_DAYS"
              :key="index"
              :label="item.value"
            >{{ item.label }}</bk-checkbox
            >
          </bk-checkbox-group>
        </bk-form-item>
        <bk-form-item :label="$t('通知方式')" property="enabled_notification_methods" required>
          <NotifyEditorTemplate
            v-if="formData.enabled_notification_methods"
            :active-methods="formData.enabled_notification_methods"
            :checkbox-info="NOTIFICATION_METHODS"
            :data-list="formData.notification_templates"
            :is-template="isAccountExpire"
            :expiring-email-key="'tenant_user_expiring'"
            :expired-email-key="'tenant_user_expired'"
            :expiring-sms-key="'tenant_user_expiring'"
            :expired-sms-key="'tenant_user_expired'"
            @handleEditorText="handleEditorText">
            <template #label>
              <div class="password-header">
                <bk-checkbox-group
                  v-model="formData.enabled_notification_methods"
                  @change="handleChange">
                  <bk-checkbox
                    v-for="(item, index) in NOTIFICATION_METHODS" :key="index"
                    :class="['password-tab', item.status ? 'active-tab' : '']"
                    style="margin-left: 5px;"
                    :label="item.value">
                    <span class="checkbox-item" @click="handleClickLabel(item)">{{item.label}}</span>
                  </bk-checkbox>
                </bk-checkbox-group>
                <div class="edit-info" @click="accountExpireTemplate">
                  <span style="font-size:14px">{{ $t('编辑通知模板') }}</span>
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
      <bk-button theme="primary" @click="changeApplication">{{ $t('应用') }}</bk-button>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { InfoBox, Message } from 'bkui-vue';
import { AngleDown, AngleUp } from 'bkui-vue/lib/icon';
import { onMounted, ref } from 'vue';

import NotifyEditorTemplate from '@/components/notify-editor/NotifyEditorTemplate.vue';
import { getTenantUserValidityPeriod, putTenantUserValidityPeriod } from '@/http/settingFiles';
import { t } from '@/language/index';
import { NOTIFICATION_METHODS, REMIND_DAYS, VALID_TIME } from '@/utils';

const isLoading = ref(false);
const formData = ref({});
const isAccountExpire = ref(false);
const isDropdownAccountExpire = ref(false);
const formRef = ref();

onMounted(() => {
  getAccountCongif();
});

const getAccountCongif = async () => {
  try {
    isLoading.value = true;
    const res = await getTenantUserValidityPeriod();
    formData.value = res.data;
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
};

const handleEditorText = (html, text, key, type) => {
  formData.value.notification_templates.forEach((item) => {
    if (item.method === type && item.scene === key) {
      item.content = text;
      item.content_html = html;
    }
  });
};

const handleClickLabel = (item) => {
  NOTIFICATION_METHODS.forEach((element) => {
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

const changeApplication = async () => {
  try {
    await formRef.value.validate();
    await putTenantUserValidityPeriod(formData.value);
    Message({ theme: 'success', message: t('更新成功') });
    getAccountCongif();
    window.changeInput = false;
  } catch (e) {
    console.warn(e);
  }
};

const changeEnabled = (value) => {
  if (!value) {
    InfoBox({
      title: t('确认要关闭账号有效期吗？'),
      subTitle: t('关闭后，存量账号有效期不变，新账号有效期永久。'),
      onClosed() {
        formData.value.enabled = !value;
      },
    });
  }
  window.changeInput = true;
};
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
