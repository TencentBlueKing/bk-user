<template>
  <bk-form
    class="data-source-content user-scroll-y"
    form-type="vertical"
    ref="formRef"
    :model="formData"
    :rules="rulesInfo"
    v-bkloading="{ loading: isLoading }">
    <div class="content-item">
      <p class="item-title">{{ $t('基本信息') }}</p>
      <bk-form-item :label="$t('数据源名称')" property="name" required>
        <bk-input
          style="width: 560px;"
          v-model="formData.name"
          :placeholder="validate.name.message"
          @focus="handleChange" />
      </bk-form-item>
      <bk-form-item label="" required>
        <bk-checkbox v-model="formData.config.enable_password" @change="changeAccountPassword">
          {{ $t('开启账密登录') }}
        </bk-checkbox>
      </bk-form-item>
    </div>
    <template v-if="formData.config.enable_password">
      <div class="content-item">
        <p class="item-title">{{ $t('密码规则') }}</p>
        <bk-form-item :label="$t('密码长度')" property="config.password_rule.min_length" required>
          <bk-input
            style="width: 200px;"
            type="number"
            :suffix="$t('至32位')"
            :min="10"
            :max="32"
            v-model="formData.config.password_rule.min_length"
            @change="handleChange"
          />
        </bk-form-item>
        <bk-form-item :label="$t('密码必须包含')" required>
          <bk-checkbox v-model="formData.config.password_rule.contain_lowercase">{{ $t('小写字母') }}</bk-checkbox>
          <bk-checkbox v-model="formData.config.password_rule.contain_uppercase">{{ $t('大写字母') }}</bk-checkbox>
          <bk-checkbox v-model="formData.config.password_rule.contain_digit">{{ $t('数字') }}</bk-checkbox>
          <bk-checkbox v-model="formData.config.password_rule.contain_punctuation">{{ $t('特殊字符（除空格）') }}</bk-checkbox>
          <p class="error-text" v-show="passwordRuleError">{{ $t('至少包含一类字符') }}</p>
        </bk-form-item>
        <bk-form-item label="" required>
          <div>
            <span>{{ $t('密码不允许连续') }}</span>
            <bk-input
              style="width: 85px;"
              type="number"
              behavior="simplicity"
              v-model="formData.config.password_rule.not_continuous_count"
            />
            <span>{{ $t('位 出现') }}</span>
          </div>
          <p class="error-text" v-show="passwordCountError">{{ $t('可选值范围：5-10') }}</p>
          <bk-checkbox v-model="formData.config.password_rule.not_keyboard_order">
            {{ $t('键盘序') }}
          </bk-checkbox>
          <bk-checkbox v-model="formData.config.password_rule.not_continuous_letter">
            {{ $t('连续字母序') }}
          </bk-checkbox>
          <bk-checkbox v-model="formData.config.password_rule.not_continuous_digit">
            {{ $t('连续数字序') }}
          </bk-checkbox>
          <bk-checkbox v-model="formData.config.password_rule.not_repeated_symbol">
            {{ $t('重复字母、数字、特殊符号') }}
          </bk-checkbox>
          <p class="error-text" v-show="passwordConfigError">{{ $t('至少包含一类连续性场景') }}</p>
        </bk-form-item>
        <bk-form-item :label="$t('密码有效期')" required>
          <bk-radio-group v-model="formData.config.password_rule.valid_time" @change="handleChange">
            <bk-radio-button
              v-for="(item, index) in VALID_TIME"
              :key="index"
              :label="item.days"
            >
              {{ item.text }}
            </bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item :label="$t('密码试错次数')" required>
          <bk-radio-group v-model="formData.config.password_rule.max_retries" @change="handleChange">
            <bk-radio-button
              v-for="(item, index) in maxTrailTimesList"
              :key="index"
              :label="item.times"
            >
              {{ item.text }}
            </bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item :label="$t('锁定时间')" property="config.password_rule.lock_time" required>
          <bk-input
            style="width: 200px;"
            type="number"
            :suffix="$t('秒')"
            :min="0"
            v-model="formData.config.password_rule.lock_time"
            @change="handleChange"
          />
        </bk-form-item>
      </div>
      <div class="content-item">
        <p class="item-title">{{ $t('初始密码设置') }}</p>
        <bk-form-item label="" required>
          <bk-checkbox
            v-model="formData.config.password_initial.force_change_at_first_login"
            @change="handleChange">
            {{ $t('首次登录强制修改密码') }}
          </bk-checkbox>
        </bk-form-item>
        <bk-form-item label="" required>
          <div class="div-flex">
            <bk-checkbox
              v-model="formData.config.password_initial.cannot_use_previous_password"
              @change="handleChange">
              {{ $t('修改密码时不能重复前') }}
            </bk-checkbox>
            <bk-input
              style="width: 85px;"
              type="number"
              behavior="simplicity"
              :min="0"
              :max="5"
              v-model="formData.config.password_initial.reserved_previous_password_count"
              @change="handleChange"
            />
            <span>{{ $t('次 用过的密码') }}</span>
          </div>
        </bk-form-item>
        <bk-form-item class="form-item-flex" :label="$t('密码生成方式')" required>
          <bk-radio-group v-model="formData.config.password_initial.generate_method" @change="handleChange">
            <bk-radio label="random">{{ $t('随机') }}</bk-radio>
            <bk-radio label="fixed">{{ $t('固定') }}</bk-radio>
          </bk-radio-group>
          <div v-if="formData.config.password_initial.generate_method === 'fixed'">
            <bk-input
              class="input-password"
              v-model="formData.config.password_initial.fixed_password"
              type="password" />
            <bk-button
              outline
              theme="primary"
              class="ml-[8px]"
              @click="handleRandomPassword">{{ $t('随机生成') }}</bk-button>
          </div>
        </bk-form-item>
        <bk-form-item
          :label="$t('通知方式')"
          :required="formData.config.password_initial.generate_method === 'random'">
          <NotifyEditorTemplate
            :active-methods="formData.config.password_initial.notification.enabled_methods"
            :checkbox-info="NOTIFICATION_METHODS"
            :data-list="formData.config.password_initial.notification.templates"
            :is-template="isPasswordInitial"
            :expiring-email-key="'user_initialize'"
            :expired-email-key="'reset_password'"
            :expiring-sms-key="'user_initialize'"
            :expired-sms-key="'reset_password'"
            :create-account-email="$t('创建账户邮件')"
            :reset-password-email="$t('重设密码后的邮件')"
            :create-account-sms="$t('创建账户短信')"
            :reset-password-sms="$t('重设密码后的短信')"
            @handleEditorText="handleEditorText">
            <template #label>
              <div class="password-header">
                <bk-checkbox-group
                  v-model="formData.config.password_initial.notification.enabled_methods"
                  @change="handleChange">
                  <bk-checkbox
                    v-for="(item, index) in NOTIFICATION_METHODS" :key="index"
                    :class="['password-tab', item.status ? 'active-tab' : '']"
                    style="margin-left: 5px;"
                    :label="item.value">
                    <span class="checkbox-item" @click="handleClickLabel(item)">{{item.label}}</span>
                  </bk-checkbox>
                </bk-checkbox-group>
                <div class="edit-info" @click="passwordInitialTemplate">
                  <span style="font-size:14px">{{ $t('编辑通知模板') }}</span>
                  <AngleUp v-if="isDropdownPasswordInitial" />
                  <AngleDown v-else />
                </div>
              </div>
            </template>
          </NotifyEditorTemplate>
          <p class="error" v-show="enabledMethodsError">{{ $t('通知方式不能为空') }}</p>
        </bk-form-item>
      </div>
      <div class="content-item">
        <p class="item-title">{{ $t('密码到期提醒') }}</p>
        <bk-form-item :label="$t('提醒时间')" property="config.password_expire.remind_before_expire" required>
          <bk-checkbox-group v-model="formData.config.password_expire.remind_before_expire" @change="handleChange">
            <bk-checkbox
              v-for="(item, index) in REMIND_DAYS"
              :key="index"
              :label="item.value"
            >{{ item.label }}</bk-checkbox
            >
          </bk-checkbox-group>
        </bk-form-item>
        <bk-form-item :label="$t('通知方式')" property="config.password_expire.notification.enabled_methods" required>
          <NotifyEditorTemplate
            :active-methods="formData.config.password_expire.notification.enabled_methods"
            :checkbox-info="NOTIFICATION_METHODS"
            :data-list="formData.config.password_expire.notification.templates"
            :is-template="isPasswordExpire"
            :expiring-email-key="'password_expiring'"
            :expired-email-key="'password_expired'"
            :expiring-sms-key="'password_expiring'"
            :expired-sms-key="'password_expired'"
            @handleEditorText="handleEditorText">
            <template #label>
              <div class="password-header">
                <bk-checkbox-group
                  v-model="formData.config.password_expire.notification.enabled_methods"
                  @change="handleChange">
                  <bk-checkbox
                    v-for="(item, index) in NOTIFICATION_METHODS" :key="index"
                    :class="['password-tab', item.status ? 'active-tab' : '']"
                    style="margin-left: 5px;"
                    :label="item.value">
                    <span class="checkbox-item" @click="handleClickLabel(item)">{{item.label}}</span>
                  </bk-checkbox>
                </bk-checkbox-group>
                <div class="edit-info" @click="passwordExpireTemplate">
                  <span style="font-size:14px">{{ $t('编辑通知模板') }}</span>
                  <AngleUp v-if="isDropdownPasswordExpire" />
                  <AngleDown v-else />
                </div>
              </div>
            </template>
          </NotifyEditorTemplate>
        </bk-form-item>
      </div>
    </template>
    <div class="btn">
      <bk-button theme="primary" class="mr8" @click="handleSubmit" :loading="btnLoading">{{ $t('提交') }}</bk-button>
      <bk-button @click="handleClickCancel">{{ $t('取消') }}</bk-button>
    </div>
  </bk-form>
</template>

<script setup lang="ts">
import { InfoBox, Message } from 'bkui-vue';
import { AngleDown, AngleUp } from 'bkui-vue/lib/icon';
import { computed, h, onMounted, reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import NotifyEditorTemplate from '@/components/notify-editor/NotifyEditorTemplate.vue';
import { useValidate } from '@/hooks';
import {
  getDataSourceDetails,
  getDefaultConfig,
  newDataSource,
  putDataSourceDetails,
  randomPasswords,
} from '@/http';
import { t } from '@/language/index';
import router from '@/router';
import { NOTIFICATION_METHODS, passwordMustIncludes, passwordNotAllowed, REMIND_DAYS, VALID_TIME } from '@/utils';

const route = useRoute();
const validate = useValidate();

const currentId = computed(() => {
  const { id } = route.params;
  return id;
});

const formRef = ref();
// 初始密码
const isPasswordInitial = ref(false);
const isDropdownPasswordInitial = ref(false);
// 密码到期
const isPasswordExpire = ref(false);
const isDropdownPasswordExpire = ref(false);
const isLoading = ref(false);
const passwordRuleError = ref(false);
const passwordCountError = ref(false);
const passwordConfigError = ref(false);
const enabledMethodsError = ref(false);

const formData = reactive({
  name: '',
  config: {},
});

const rulesInfo = {
  name: [validate.required, validate.name],
  min_length: [validate.required],
};

onMounted(async () => {
  isLoading.value = true;
  try {
    if (currentId.value) {
      const res = await getDataSourceDetails(currentId.value);
      formData.name = res?.data?.name;
      if (!res?.data?.plugin_config?.enable_password) {
        const demo = await getDefaultConfig(route.params.type);
        formData.config = {
          ...demo?.data?.config,
          enable_password: false,
        };
      } else {
        formData.config = res?.data?.plugin_config;
      }
    } else {
      const res = await getDefaultConfig(route.params.type);
      formData.config = res?.data?.config;
    }
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});

watch(() => formData.config?.password_rule, (value) => {
  if (!value) return;
  const list = Object.entries(value).filter(([key]) => passwordMustIncludes[key]);
  const list2 = Object.entries(value).filter(([key]) => passwordNotAllowed[key]);

  passwordRuleError.value = !list.some(([, val]) => val);
  passwordConfigError.value = !list2.some(([, val]) => val);

  const count = formData.config?.password_rule?.not_continuous_count;
  const isCountInRange = count >= 5 && count <= 10;

  if (!passwordConfigError.value && isCountInRange) {
    passwordCountError.value = false;
  } else if (!passwordConfigError.value && !isCountInRange) {
    passwordCountError.value = !isCountInRange;
  } else {
    passwordCountError.value = count === 0 && !passwordConfigError.value;
    passwordConfigError.value = count !== 0 && passwordConfigError.value;
  }
}, { deep: true });

watch(() => formData.config?.password_rule?.not_continuous_count, (value, oldVal) => {
  if (!value) return;
  if (value !== oldVal) {
    window.changeInput = true;
  }
  const list = Object.entries(formData.config?.password_rule)
    .filter(([key, val]) => passwordNotAllowed[key] && val)
    .map(val => val);

  if (value === 0) return;

  const isValueInRange = value >= 5 && value <= 10;
  passwordCountError.value = !isValueInRange;
  passwordConfigError.value = !!list.every(v => !v);
});

watch(() => formData.config?.password_initial?.generate_method, (value) => {
  enabledMethodsError.value = value === 'random' && !formData.config.password_initial.notification.enabled_methods.length;
  if (value === 'random') {
    formData.config.password_initial.fixed_password = null;
  }
});

watch(() => formData.config?.password_initial?.notification?.enabled_methods, (value) => {
  if (formData.config?.password_initial?.generate_method === 'fixed') {
    return enabledMethodsError.value = false;
  }
  enabledMethodsError.value = !value.length;
});

const maxTrailTimesList = reactive([
  { times: 3, text: `3 ${t('次')}` },
  { times: 5, text: `5 ${t('次')}` },
  { times: 10, text: `10 ${t('次')}` },
]);

const handleEditorText = (html, text, key, type) => {
  const templates = ref(key === 'password_expiring' || key === 'password_expired'
    ? formData.config.password_expire.notification.templates
    : formData.config.password_initial.notification.templates);
  templates.value.forEach((item) => {
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

const passwordInitialTemplate = () => {
  isPasswordInitial.value = !isPasswordInitial.value;
  isDropdownPasswordInitial.value = !isDropdownPasswordInitial.value;
};

const passwordExpireTemplate = () => {
  isPasswordExpire.value = !isPasswordExpire.value;
  isDropdownPasswordExpire.value = !isDropdownPasswordExpire.value;
};

const handleClickCancel = () => {
  router.go(-1);
};

const btnLoading = ref(false);
const handleSubmit = async () => {
  try {
    if (passwordRuleError.value
      || passwordCountError.value
      || passwordConfigError.value
      || enabledMethodsError.value) return;
    await formRef.value.validate();
    btnLoading.value = true;
    const params = {
      name: formData.name,
      plugin_id: route.params.type,
      field_mapping: [],
    };
    if (formData.config.enable_password) {
      params.plugin_config = {
        password_rule: formData.config.password_rule,
        password_initial: formData.config.password_initial,
        password_expire: formData.config.password_expire,
        enable_password: formData.config.enable_password,
      };
    } else {
      params.plugin_config = {
        password_rule: null,
        password_initial: null,
        password_expire: null,
        enable_password: false,
      };
    }
    currentId.value ? updateDataSource(params) : getDataSource(params);
  } catch (e) {
    console.warn(e);
  } finally {
    btnLoading.value = false;
  }
};

const updateDataSource = async (params) => {
  const data = {
    id: currentId.value,
    name: params.name,
    field_mapping: params.field_mapping,
    plugin_config: params.plugin_config,
  };
  await putDataSourceDetails(data);
  window.changeInput = false;
  router.push({ name: 'local' });
  Message({
    theme: 'success',
    message: t('数据源更新成功'),
  });
};

const getDataSource = async (params) => {
  await newDataSource(params);
  window.changeInput = false;
  router.push({ name: 'local' });
  Message({
    theme: 'success',
    message: t('数据源创建成功'),
  });
};

const handleChange = () => {
  window.changeInput = true;
};

const changeAccountPassword = (value) => {
  if (!value) {
    InfoBox({
      title: t('确认要关闭账密登录吗？'),
      subTitle: h('div', {
        style: {
          textAlign: 'left',
          lineHeight: '24px',
        },
      }, [
        h('p', t('1.关闭后该数据的用户将无法通过账密登录')),
        h('p', t('2.关闭后，再次开启时，账密规则信息会重置')),
      ]),
      onClosed() {
        formData.config.enable_password = !value;
      },
    });
  }
  window.changeInput = true;
};

const handleRandomPassword = async () => {
  try {
    const passwordRes = await randomPasswords({});
    formData.config.password_initial.fixed_password = passwordRes.data.password;
    window.changeInput = true;
  } catch (e) {
    console.warn(e);
  }
};
</script>

<style lang="less" scoped>
@import url('@/components/notify-editor/NotifyEditor.less');
@import url('./index.less');

.prefix-slot {
  display: flex;
  width: 80px;
  cursor: pointer;
  background: #e1ecff;
  align-items: center;
  justify-content: center;
}

.error {
  position: absolute;
  left: 0;
  padding-top: 4px;
  font-size: 12px;
  line-height: 1;
  color: #ea3636;
  text-align: left;
  animation: form-error-appear-animation 0.15s;
}
</style>
