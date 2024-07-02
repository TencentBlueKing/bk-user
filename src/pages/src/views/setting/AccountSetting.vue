<template>
  <div v-if="isEdit" class="account-setting-wrapper user-scroll-y">
    <bk-form class="account-setting-content" form-type="vertical" :model="formData" ref="formRef">
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
        <div v-if="isShowItem">
          <bk-form-item :label="$t('到期提醒时间')" property="remind_before_expire" required>
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
            @handle-editor-text="handleEditorText">
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
      <bk-button
        class="min-w-[88px] mr-[8px]"
        theme="primary"
        @click="changeApplication"
        :disabled="isDisabled"
      >
        {{ $t('保存') }}
      </bk-button>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        @click="cancelEdit"
      >
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
  <div v-else style="padding: 24px;">
    <Row title="">
      <div class="flex items-top justify-between">
        <div>
          <LabelContent :label="$t('账号有效期')">
            {{ validityPeriod}}
          </LabelContent>
          <LabelContent :label="$t('到期提醒时间')">{{ remindBeforeBxpire}}</LabelContent>
          <LabelContent :label="$t('通知方式')">{{ enabledNotificationMethods}}</LabelContent>
        </div>
        <bk-button
          class="min-w-[64px]"
          outline
          theme="primary"
          @click="isEdit = true"
        >
          {{ $t('编辑') }}
        </bk-button>
      </div>
    </Row>
  </div>
</template>

<script setup lang="ts">
import { InfoBox, Message } from 'bkui-vue';
import { AngleDown, AngleUp } from 'bkui-vue/lib/icon';
import { computed, onMounted, ref, watch } from 'vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import Row from '@/components/layouts/row.vue';
import NotifyEditorTemplate from '@/components/notify-editor/NotifyEditorTemplate.vue';
import { getTenantUserValidityPeriod, putTenantUserValidityPeriod } from '@/http';
import { t } from '@/language/index';
import { useMainViewStore } from '@/store';
import { NOTIFICATION_METHODS, REMIND_DAYS, VALID_TIME } from '@/utils';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const isLoading = ref(false);
const formData = ref({});
const isAccountExpire = ref(false);
const isDropdownAccountExpire = ref(false);
const formRef = ref();
const isEdit = ref(false);
const isDisabled = ref(true);
let originalData = {};
const isChangeValidityPeriod = ref(false)

onMounted(() => {
  getAccountCongif();
});

watch(formData, () => {
  isDisabled.value = JSON.stringify(originalData)  === JSON.stringify(formData.value);
}, { deep: true });

watch(() =>formData.value.validity_period, () => {
  isChangeValidityPeriod.value = originalData.validity_period  !== formData.value.validity_period});

const validityPeriod = computed(() => VALID_TIME.find(item => item?.days === formData.value.validity_period)?.text);

const remindBeforeBxpire = computed(() => findLabelsByValues(formData.value.remind_before_expire, REMIND_DAYS));

const enabledNotificationMethods = computed(() => findLabelsByValues(formData.value.enabled_notification_methods, NOTIFICATION_METHODS));

const isShowItem = computed(() => formData.value.validity_period !== -1 );

const findLabelsByValues = (values, array) => values?.map((value) => {
  const item = array.find(item => item.value === value);
  return item?.label ?? '';
})?.join(', ') ?? '';

const cancelEdit = () => {
  isEdit.value = false;
  getAccountCongif();
};

const getAccountCongif = async () => {
  try {
    isLoading.value = true;
    const res = await getTenantUserValidityPeriod();
    formData.value = res.data;
    originalData = JSON.parse(JSON.stringify(res.data));
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

const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    await putTenantUserValidityPeriod(formData.value);
    Message({ theme: 'success', message: t('更新成功') });
    cancelEdit()
    window.changeInput = false;
  } catch (e) {
    console.warn(e);
  }
};

const changeApplication = () => {
  if (isChangeValidityPeriod.value) {
    InfoBox({
      title: t('确认要修改账号有效期吗？'),
      subTitle: t('当前配置将对新账号生效，存量账号的有效期不变。'),
      onConfirm: handleSubmit
    });
  } else {
    handleSubmit()
  }
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
