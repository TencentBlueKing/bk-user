<template>
  <div class="details-wrapper">
    <bk-form
      class="px-[24px] pt-[24px] pb-[60px]"
      form-type="vertical"
      ref="formRef"
      :model="formData"
      :rules="rulesInfo"
      v-bkloading="{ loading: isLoading }">
      <Row :title="$t('基本信息')">
        <bk-form-item :label="$t('名称')" property="name" required>
          <bk-input
            style="width: 600px;"
            v-model="formData.name"
            :placeholder="validate.loginName.message"
            @focus="handleChange" />
        </bk-form-item>
        <bk-form-item :label="$t('是否启用')" required>
          <bk-switcher
            :value="formData.config?.enable_password"
            theme="primary"
            size="large"
            @change="changeAccountPassword"
          />
        </bk-form-item>
      </Row>
      <EffectiveScopeEditor
        v-model="formData.scopeIds"
        local-only
        @change="handleChange"
      />
      <Row :title="$t('密码规则')" v-if="formData.config?.password_rule">
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
          <bk-checkbox-group v-model="mustIncludeList" @change="handleMustIncludeRuleChange">
            <bk-checkbox
              v-for="opt in mustIncludeOptions"
              :key="opt.label"
              :label="opt.label">
              {{ $t(opt.text) }}
            </bk-checkbox>
          </bk-checkbox-group>
          <p class="error-text" v-show="passwordRuleError">{{ $t('至少包含一类字符') }}</p>
        </bk-form-item>
        <bk-form-item label="" required>
          <div class="div-flex">
            <span>{{ $t('密码不允许连续') }}</span>
            <bk-input
              style="width: 85px;"
              type="number"
              behavior="simplicity"
              :min="0"
              :max="10"
              v-model="formData.config.password_rule.not_continuous_count"
              @input="handleNotContinuousCountInput"
            />
            <span>{{ $t('位 出现') }}</span>
          </div>
          <p
            v-show="passwordCountError"
            class="error-text"
          >
            {{ $t('可选值范围：0（不限制）或 3-10') }}
          </p>
          <bk-checkbox-group
            v-model="continuousRuleList"
            @change="triggerPasswordConfigValidate"
          >
            <bk-checkbox
              v-for="opt in continuousOptions"
              :key="opt.label"
              :label="opt.label"
              :disabled="isContinuousDisabled"
            >
              {{ $t(opt.text) }}
            </bk-checkbox>
          </bk-checkbox-group>
          <p class="error-text" v-show="passwordConfigError">{{ $t('至少包含一类连续性场景') }}</p>
        </bk-form-item>
      </Row>
      <Row :title="$t('初始密码设置')" v-if="formData.config?.password_initial">
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
            <passwordInput
              v-model="formData.config.password_initial.fixed_password"
              :is-password-disabled="isInputEyesDisabled"
              :is-fast-clear-enable="isInputEyesDisabled"
              @input="inputPassword" />
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
            @handle-editor-text="handleEditorText">
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
      </Row>
      <Row :title="$t('登录限制')" v-if="formData.config?.login_limit">
        <bk-form-item label="" required>
          <bk-checkbox
            v-model="formData.config.login_limit.force_change_at_first_login"
            @change="handleChange">
            {{ $t('首次登录强制修改密码') }}
          </bk-checkbox>
        </bk-form-item>
        <bk-form-item :label="$t('密码试错次数')" required>
          <bk-radio-group v-model="formData.config.login_limit.max_retries" @change="handleChange">
            <bk-radio-button
              v-for="(item, index) in maxTrailTimesList"
              :key="index"
              :label="item.times"
            >
              {{ item.text }}
            </bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item :label="$t('锁定时间')" property="config.login_limit.lock_time" required>
          <bk-input
            style="width: 200px;"
            type="number"
            :suffix="$t('秒')"
            :min="0"
            v-model="formData.config.login_limit.lock_time"
            @change="handleChange"
          />
        </bk-form-item>
      </Row>
      <Row :title="$t('密码有效期设置')" v-if="formData.config?.password_expire">
        <bk-form-item :label="$t('密码有效期')" required>
          <bk-radio-group v-model="formData.config.password_expire.valid_time" @change="handleChange">
            <bk-radio-button
              v-for="(item, index) in VALID_TIME"
              :key="index"
              :label="item.days"
            >
              {{ item.text }}
            </bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item :label="$t('到期提醒时间')" property="config.password_expire.remind_before_expire" required>
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
            @handle-editor-text="handleEditorText">
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
      </Row>
    </bk-form>
    <div class="footer">
      <bk-button theme="primary" class="mr8" @click="handleSubmit" :loading="btnLoading" :disabled="isDisabled">
        {{ $t('提交') }}
      </bk-button>
      <bk-button @click="emit('cancel')">{{ $t('取消') }}</bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { InfoBox } from 'bkui-vue';
import { AngleDown, AngleUp } from 'bkui-vue/lib/icon';
import { computed, onMounted, reactive, ref, watch } from 'vue';

import EffectiveScopeEditor from './EffectiveScopeEditor.vue';

import Row from '@/components/layouts/ItemRow.vue';
import NotifyEditorTemplate from '@/components/notify-editor/NotifyEditorTemplate.vue';
import passwordInput from '@/components/passwordInput.vue';
import { useValidate } from '@/hooks';
import {
  getDefaultConfig,
  postLocalIdps,
  putLocalIdps,
  randomPasswords,
} from '@/http';
import { LocalIdpDetail, LocalIdpPluginConfig, NewLocalIdpsParams } from '@/http/types/authSourceFiles';
import { t } from '@/language/index';
import { NOTIFICATION_METHODS, passwordMustIncludes, passwordNotAllowed, REMIND_DAYS, VALID_TIME } from '@/utils';

interface IProps {
  data?: LocalIdpDetail;
}
const props = defineProps<IProps>();

const emit = defineEmits(['cancel', 'success']);

const validate = useValidate();

const rulesInfo = {
  name: [validate.required, validate.loginName],
  min_length: [validate.required],
};

// 不允许连续场景的复选项，key 需与 password_rule 字段一致
const continuousOptions = [
  { label: 'not_keyboard_order', text: '键盘序' },
  { label: 'not_continuous_letter', text: '连续字母序' },
  { label: 'not_continuous_digit', text: '连续数字序' },
  { label: 'not_repeated_symbol', text: '重复字母、数字、特殊符号' },
];

/**
 * 密码必须包含的复选项，key 需与 password_rule 字段一致
 * bk-checkbox-group 绑定数组与接口布尔字段的转换
 */
const mustIncludeOptions = [
  { label: 'contain_lowercase', text: '小写字母' },
  { label: 'contain_uppercase', text: '大写字母' },
  { label: 'contain_digit', text: '数字' },
  { label: 'contain_punctuation', text: '特殊字符（除空格）' },
];

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
let originalData = {};
const isDisabled = ref(true);
const isInputEyesDisabled = ref(false);

const formData = reactive({
  name: '',
  status: '',
  config: {} as LocalIdpPluginConfig,
  scopeIds: [],
});

const maxTrailTimesList = reactive([
  { times: 3, text: `3 ${t('次')}` },
  { times: 5, text: `5 ${t('次')}` },
  { times: 10, text: `10 ${t('次')}` },
]);

const isContinuousDisabled = computed(() => Number(formData.config?.password_rule?.not_continuous_count) === 0);

const mustIncludeList = computed({
  get: () => {
    const rule = formData.config?.password_rule;
    if (!rule) return [];
    return mustIncludeOptions.filter(opt => rule[opt.label]).map(opt => opt.label);
  },
  set: (value: string[]) => {
    const rule = formData.config?.password_rule;
    if (!rule) return;
    mustIncludeOptions.forEach((opt) => {
      rule[opt.label] = value.includes(opt.label);
    });
  },
});

// bk-checkbox-group 绑定数组与接口布尔字段的转换
const continuousRuleList = computed({
  get: () => {
    const rule = formData.config?.password_rule;
    if (!rule) return [];
    return continuousOptions.filter(opt => rule[opt.label]).map(opt => opt.label);
  },
  set: (value: string[]) => {
    const rule = formData.config?.password_rule;
    if (!rule) return;
    continuousOptions.forEach((opt) => {
      rule[opt.label] = value.includes(opt.label);
    });
  },
});

const btnLoading = ref(false);

// 编辑通知方式
const handleEditorText = (html: string, text: string, key: string, type: string) => {
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

const handleClickLabel = (item: typeof NOTIFICATION_METHODS[number]) => {
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

const handleSubmit = async () => {
  try {
    if (passwordRuleError.value
      || passwordCountError.value
      || passwordConfigError.value
      || enabledMethodsError.value) return;
    const valid = await formRef.value?.validate?.().catch(() => false);
    if (!valid) return;
    btnLoading.value = true;
    const params: NewLocalIdpsParams = {
      name: formData.name,
      status: formData.config?.enable_password ? 'enabled' : 'disabled',
      plugin_config: formData.config,
      data_source_match_rules: formData.scopeIds.map(id => ({
        data_source_id: id,
      })),
    };
    if (props.data?.id) {
      params.id = props.data?.id;
      await putLocalIdps(params);
      emit('success', formData.config?.enable_password);
    } else {
      await postLocalIdps(params);
      emit('success', formData.config?.enable_password);
    }
  } catch (e) {
    console.warn(e);
  } finally {
    btnLoading.value = false;
  }
};

const handleChange = () => {
  window.changeInput = true;
};

const changeAccountPassword = (value: boolean) => {
  if (!value) {
    InfoBox({
      title: t('确认要关闭账密登录吗？'),
      subTitle: t('关闭后用户将无法通过账密登录'),
      onConfirm() {
        formData.config.enable_password = value;
      },
      onCancel() {
        formData.config.enable_password = !value;
      },
      quickClose: false,
    });
  } else {
    formData.config.enable_password = value;
  }
  window.changeInput = true;
};

const handleRandomPassword = async () => {
  try {
    const params = { password_rule_config: formData.config?.password_rule };
    const passwordRes = await randomPasswords(params);
    formData.config.password_initial.fixed_password = passwordRes.data.password;
    window.changeInput = true;
  } catch (e) {
    console.warn(e);
  }
};

/** 密码生成方式 - 固定时是否禁用eyes */
const setIsIntPutEyesDisabled = (fixed_password: string) => {
  isInputEyesDisabled.value = !!fixed_password;
};

const inputPassword = (val: string) => {
  formData.config.password_initial.fixed_password = val;
};

/** 密码不能连续出现的次数 */
function handleNotContinuousCountInput(value) {
  // 空字符串/undefined/null 视为不合法
  if (value === '' || value === undefined || value === null) {
    passwordCountError.value = true;
    triggerPasswordConfigValidate();
    return;
  }
  const numValue = Number(value);
  const isValueInRange = numValue === 0 || (numValue >= 3 && numValue <= 10);
  passwordCountError.value = !isValueInRange;
  triggerPasswordConfigValidate();
  if (numValue === 0) {
    continuousRuleList.value = [];
    passwordConfigError.value = false;
  }
}

/** 密码规则 */
function triggerPasswordConfigValidate() {
  const list = Object.entries(formData.config?.password_rule)
    .filter(([key, val]) => passwordNotAllowed[key] && val)
    .map(val => val);
  // 密码不能连续出现的次数不为0时，必须选择至少一个密码不能连续出现的规则
  if (formData.config?.password_rule?.not_continuous_count !== 0) {
    passwordConfigError.value = !!list.every(v => !v);
  }
}
/** 密码必须包含规则校验 */
function handleMustIncludeRuleChange() {
  const list = Object.entries(formData.config?.password_rule)
    .filter(([key, val]) => passwordMustIncludes[key] && val);
  passwordRuleError.value = !list.some(([, val]) => val);
}

let isInitialized = false;

watch(formData, () => {
  if (!isInitialized) return;
  isDisabled.value = props?.data?.id ? JSON.stringify(originalData) === JSON.stringify(formData) : false;
  window.changeInput = !isDisabled.value;
}, { deep: true });

// 监听密码生成方式
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

onMounted(async () => {
  isLoading.value = true;
  try {
    if (props.data?.id) {
      // 从查看态传入的详情数据直接回填，避免重复请求
      formData.name = props.data.name;
      formData.status = props.data.status;
      formData.config = props.data.plugin_config;
      if (props.data.data_source_match_rules?.length) {
        formData.scopeIds = props.data.data_source_match_rules.map(item => item.data_source_id);
      }
    } else {
      // 新增态：回填认证源名称（父组件传入的默认对象）
      formData.name = props.data?.name || '';
      // 新增本地认证源：本地认证源依赖本地数据源（未配置本地数据源时无法进入此表单），
      // 其密码规则等配置继承自 local 插件的默认配置，需走接口获取；
      // 其他认证源（WeCom/Custom）的 plugin_config 结构固定，在组件内初始化默认结构即可，无需请求
      const res = await getDefaultConfig('local');
      formData.config = (res?.data?.config || {})  as LocalIdpPluginConfig;
      formData.config.enable_password = true;
    }
    originalData = JSON.parse(JSON.stringify(formData));
    isInitialized = true;

    setIsIntPutEyesDisabled(formData.config?.password_initial?.fixed_password);
    handleMustIncludeRuleChange();
    triggerPasswordConfigValidate();
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style lang="less" scoped>
@import url('@/components/notify-editor/NotifyEditor.less');
@import url('./Local.less');

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
