<template>
  <bk-form
    ref="formRef"
    :model="config"
    :rules="rules"
    form-type="vertical"
    class="flex flex-col divide-y divide-[#EAEBF0]"
  >
    <Row :title="$t('启用密码规则')" class="!pb-[16px]">
      <template #header>
        <!-- 仅在「被引用 + 开关当前开启」的锁定态展示 tooltip，正常状态不展示 -->
        <bk-switcher
          v-model="enablePassword"
          theme="primary"
          class="!ml-[12px]"
          :disabled="isPasswordRuleSwitchLocked"
          v-bk-tooltips="{
            content: $t('已被本地账密的生效范围引用，无法关闭'),
            disabled: !isPasswordRuleSwitchLocked,
            placement: 'right'
          }"
          @change="handleEnablePasswordChange"
        />
      </template>
      <p class="text-[12px] text-[#979BA5] -mt-[8px]">
        {{ switchDescription }}
      </p>
    </Row>
    <!-- 密码相关配置（密码规则/初始密码/登录限制/密码有效期）存储于本地数据源 plugin_config，
     取数与提交均走数据源详情接口（getDataSourceDetails / putDataSourceDetails） -->
    <template v-if="enablePassword && config">
      <Row :title="$t('密码规则')" v-if="config?.password_rule">
        <bk-form-item :label="$t('密码长度')" property="password_rule.min_length" required>
          <bk-input
            style="width: 200px;"
            type="number"
            :suffix="$t('至32位')"
            :min="10"
            :max="32"
            v-model="config.password_rule.min_length"
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
            <!-- 增减按钮只 emit change 不 emit input（bkui-vue handleInc），input/change 双绑覆盖所有改值路径，重复校验幂等 -->
            <bk-input
              style="width: 85px;"
              type="number"
              behavior="simplicity"
              :min="0"
              :max="10"
              v-model="config.password_rule.not_continuous_count"
              @input="handleNotContinuousCountInput"
              @change="handleNotContinuousCountInput"
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
      <Row :title="$t('初始密码设置')" v-if="config?.password_initial">
        <bk-form-item label="" required>
          <div class="div-flex">
            <bk-checkbox
              v-model="config.password_initial.cannot_use_previous_password"
              @change="handleChange">
              {{ $t('修改密码时不能重复前') }}
            </bk-checkbox>
            <bk-input
              style="width: 85px;"
              type="number"
              behavior="simplicity"
              :min="0"
              :max="5"
              v-model="config.password_initial.reserved_previous_password_count"
              @change="handleChange"
            />
            <span>{{ $t('次 用过的密码') }}</span>
          </div>
        </bk-form-item>
        <bk-form-item class="form-item-flex" :label="$t('密码生成方式')" required>
          <bk-radio-group v-model="config.password_initial.generate_method" @change="handleChange">
            <bk-radio label="random">{{ $t('随机') }}</bk-radio>
            <bk-radio label="fixed">{{ $t('固定') }}</bk-radio>
          </bk-radio-group>
          <div v-if="config.password_initial.generate_method === 'fixed'">
            <passwordInput
              v-model="config.password_initial.fixed_password"
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
          :required="config.password_initial.generate_method === 'random'">
          <NotifyEditorTemplate
            :active-methods="config.password_initial.notification.enabled_methods"
            :checkbox-info="NOTIFICATION_METHODS"
            :data-list="config.password_initial.notification.templates"
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
                  v-model="config.password_initial.notification.enabled_methods"
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
      <Row :title="$t('登录限制')" v-if="config?.login_limit">
        <bk-form-item label="" required>
          <bk-checkbox
            v-model="config.login_limit.force_change_at_first_login"
            @change="handleChange">
            {{ $t('首次登录强制修改密码') }}
          </bk-checkbox>
        </bk-form-item>
        <bk-form-item :label="$t('密码试错次数')" required>
          <bk-radio-group v-model="config.login_limit.max_retries" @change="handleChange">
            <bk-radio-button
              v-for="(item, index) in maxTrailTimesList"
              :key="index"
              :label="item.times"
            >
              {{ item.text }}
            </bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item :label="$t('锁定时间')" property="login_limit.lock_time" required>
          <bk-input
            style="width: 200px;"
            type="number"
            :suffix="$t('秒')"
            :min="0"
            v-model="config.login_limit.lock_time"
            @change="handleChange"
          />
        </bk-form-item>
      </Row>
      <Row :title="$t('密码有效期设置')" v-if="config?.password_expire">
        <bk-form-item :label="$t('密码有效期')" required>
          <bk-radio-group v-model="config.password_expire.valid_time" @change="handleChange">
            <bk-radio-button
              v-for="(item, index) in VALID_TIME"
              :key="index"
              :label="item.days"
            >
              {{ item.text }}
            </bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item :label="$t('到期提醒时间')" property="password_expire.remind_before_expire" required>
          <bk-checkbox-group
            v-model="config.password_expire.remind_before_expire"
            @change="handleChange"
          >
            <bk-checkbox
              v-for="(item, index) in REMIND_DAYS"
              :key="index"
              :label="item.value"
            >{{ item.label }}</bk-checkbox
            >
          </bk-checkbox-group>
        </bk-form-item>
        <bk-form-item
          :label="$t('通知方式')"
          property="password_expire.notification.enabled_methods"
          required
        >
          <NotifyEditorTemplate
            :active-methods="config.password_expire.notification.enabled_methods"
            :checkbox-info="NOTIFICATION_METHODS"
            :data-list="config.password_expire.notification.templates"
            :is-template="isPasswordExpire"
            :expiring-email-key="'password_expiring'"
            :expired-email-key="'password_expired'"
            :expiring-sms-key="'password_expiring'"
            :expired-sms-key="'password_expired'"
            @handle-editor-text="handleEditorText">
            <template #label>
              <div class="password-header">
                <bk-checkbox-group
                  v-model="config.password_expire.notification.enabled_methods"
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
    </template>
  </bk-form>
</template>

<script setup lang="ts">
import { AngleDown, AngleUp } from 'bkui-vue/lib/icon';
import { computed, ref, watch } from 'vue';

import Row from '@/components/layouts/ItemRow.vue';
import NotifyEditorTemplate from '@/components/notify-editor/NotifyEditorTemplate.vue';
import passwordInput from '@/components/passwordInput.vue';
import { useValidate } from '@/hooks';
import { randomPasswords } from '@/http';
import { getDefaultConfig } from '@/http/dataSourceFiles';
import { LocalDataSourcePluginConfig } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';
import { NOTIFICATION_METHODS, passwordMustIncludes, passwordNotAllowed, REMIND_DAYS, VALID_TIME } from '@/utils';

interface Props {
  /** 生效范围引用锁定：被引用后不允许关闭密码规则开关 */
  isPasswordRuleSwitchLocked?: boolean;
}

const config = defineModel<LocalDataSourcePluginConfig>('config', { required: true });

withDefaults(defineProps<Props>(), {
  isPasswordRuleSwitchLocked: false,
});

const formRef = ref();
const isPasswordInitial = ref(false);
const isDropdownPasswordInitial = ref(false);
const isPasswordExpire = ref(false);
const isDropdownPasswordExpire = ref(false);
const isInputEyesDisabled = ref(false);
const passwordRuleError = ref(false);
const passwordCountError = ref(false);
const passwordConfigError = ref(false);
const enabledMethodsError = ref(false);

const maxTrailTimesList = [
  { times: 3, text: `3 ${t('次')}` },
  { times: 5, text: `5 ${t('次')}` },
  { times: 10, text: `10 ${t('次')}` },
];

// 不允许连续场景的复选项，key 需与 password_rule 字段一致
const continuousOptions: { label: 'not_keyboard_order' | 'not_continuous_letter' | 'not_continuous_digit' | 'not_repeated_symbol'; text: string }[] = [
  { label: 'not_keyboard_order', text: '键盘序' },
  { label: 'not_continuous_letter', text: '连续字母序' },
  { label: 'not_continuous_digit', text: '连续数字序' },
  { label: 'not_repeated_symbol', text: '重复字母、数字、特殊符号' },
];

/**
 * 密码必须包含的复选项，key 需与 password_rule 字段一致
 * bk-checkbox-group 绑定数组与接口布尔字段的转换
 */
const mustIncludeOptions: { label: 'contain_lowercase' | 'contain_uppercase' | 'contain_digit' | 'contain_punctuation'; text: string }[] = [
  { label: 'contain_lowercase', text: '小写字母' },
  { label: 'contain_uppercase', text: '大写字母' },
  { label: 'contain_digit', text: '数字' },
  { label: 'contain_punctuation', text: '特殊字符（除空格）' },
];

const validate = useValidate();
const rules = {
  // key 需与 form-item 的 property 完整路径一致，否则规则无法命中
  'password_rule.min_length': [validate.required],
};

const enablePassword = computed({
  get: () => config.value?.enable_password ?? false,
  set: (value: boolean) => {
    if (config.value) {
      config.value.enable_password = value;
    }
  },
});

// 开关描述按状态切换：开启说明密码用途，关闭提示影响与后续开启入口
const switchDescription = computed(() => (enablePassword.value
  ? t('该数据源的用户可以通过账号密码登录，以下规则会用于生成和校验密码')
  : t('未启用时，该数据源的用户不能通过账密登录，之后可在编辑页开启')));
const isContinuousDisabled = computed(() => Number(config.value?.password_rule?.not_continuous_count) === 0);

const mustIncludeList = computed({
  get: () => {
    const rule = config.value?.password_rule;
    if (!rule) return [];
    return mustIncludeOptions.filter(opt => rule[opt.label]).map(opt => opt.label);
  },
  set: (value: string[]) => {
    const rule = config.value?.password_rule;
    if (!rule) return;
    mustIncludeOptions.forEach((opt) => {
      rule[opt.label] = value.includes(opt.label);
    });
  },
});

// bk-checkbox-group 绑定数组与接口布尔字段的转换
const continuousRuleList = computed({
  get: () => {
    const rule = config.value?.password_rule;
    if (!rule) return [];
    return continuousOptions.filter(opt => rule[opt.label]).map(opt => opt.label);
  },
  set: (value: string[]) => {
    const rule = config.value?.password_rule;
    if (!rule) return;
    continuousOptions.forEach((opt) => {
      rule[opt.label] = value.includes(opt.label);
    });
  },
});

const handleChange = () => {
  window.changeInput = true;
};

// 编辑通知方式
const handleEditorText = (html: string, text: string, key: string, type: string) => {
  const templates = key === 'password_expiring' || key === 'password_expired'
    ? config.value?.password_expire?.notification?.templates ?? []
    : config.value?.password_initial?.notification?.templates ?? [];
  templates.forEach((item) => {
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

const handleRandomPassword = async () => {
  try {
    const params = { password_rule_config: config.value.password_rule };
    const passwordRes = await randomPasswords(params);
    config.value.password_initial.fixed_password = passwordRes.data.password;
    window.changeInput = true;
  } catch (e) {
    console.warn(e);
  }
};

// 密码生成方式 - 固定时是否禁用eyes
const setIsIntPutEyesDisabled = (fixed_password: string) => {
  isInputEyesDisabled.value = !!fixed_password;
};

const inputPassword = (val: string) => {
  config.value.password_initial.fixed_password = val;
};

// 密码不能连续出现的次数
const handleNotContinuousCountInput = (value: string | number) => {
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
};

// 密码规则
const triggerPasswordConfigValidate = () => {
  // 未启用密码规则时跳过校验
  if (!enablePassword.value) return;
  const enabledRules = Object.entries(config.value?.password_rule ?? {})
    .filter(([key, val]) => passwordNotAllowed[key as keyof typeof passwordNotAllowed] && val);
  // 密码不能连续出现的次数不为0时，必须选择至少一个密码不能连续出现的规则
  if (config.value?.password_rule?.not_continuous_count !== 0) {
    passwordConfigError.value = enabledRules.length === 0;
  }
};
// 密码必须包含规则校验
const handleMustIncludeRuleChange = () => {
  if (!enablePassword.value) return;
  const list = Object.entries(config.value?.password_rule ?? {})
    .filter(([key, val]) => passwordMustIncludes[key as keyof typeof passwordMustIncludes] && val);
  passwordRuleError.value = !list.some(([, val]) => val);
};

// 切换密码规则开关：开启时补齐缺失的配置段并重新执行组合校验
const handleEnablePasswordChange = async (value: boolean) => {
  window.changeInput = true;
  if (!value || !config.value) return;
  const currentConfig = config.value;
  // 关闭状态下后端允许配置段为 null，开启前用插件默认配置补齐，保证表单可填写
  const hasEmptySection = !currentConfig.password_rule
    || !currentConfig.password_initial
    || !currentConfig.password_expire
    || !currentConfig.login_limit;
  if (hasEmptySection) {
    try {
      const res = await getDefaultConfig('local');
      const defaults = res?.data?.config as LocalDataSourcePluginConfig;
      currentConfig.password_rule ??= defaults?.password_rule;
      currentConfig.password_initial ??= defaults?.password_initial;
      currentConfig.password_expire ??= defaults?.password_expire;
      currentConfig.login_limit ??= defaults?.login_limit;
    } catch (e) {
      // 补齐失败回滚开关，避免提交 enable_password: true + 空配置段
      enablePassword.value = false;
      console.error(e);
      return;
    }
  }
  handleMustIncludeRuleChange();
  triggerPasswordConfigValidate();
};

/**
 * 密码相关组合校验：必须包含/连续性规则/连续次数/通知方式，任一不合法则阻止提交
 * 未启用密码规则时不参与校验（此时密码配置区块不展示）
 */
const validatePasswordConfig = () => !enablePassword.value || (
  !passwordRuleError.value
  && !passwordCountError.value
  && !passwordConfigError.value
  && !enabledMethodsError.value
);

/** 表单 + 密码组合校验，供容器在「完成 / 保存」前调用 */
const handleValidate = async () => {
  handleMustIncludeRuleChange();
  triggerPasswordConfigValidate();
  const valid = await formRef.value?.validate().catch(() => false) ?? false;
  return valid && validatePasswordConfig();
};

// 监听密码生成方式
watch(() => config.value?.password_initial?.generate_method, (value) => {
  enabledMethodsError.value = value === 'random'
    && !(config.value?.password_initial?.notification?.enabled_methods ?? []).length;
  if (value === 'random') {
    config.value.password_initial.fixed_password = null;
  }
});

watch(() => config.value?.password_initial?.notification?.enabled_methods, (value) => {
  if (config.value?.password_initial?.generate_method === 'fixed') {
    return enabledMethodsError.value = false;
  }
  enabledMethodsError.value = !(value ?? []).length;
});

// 配置对象被容器整体替换（编辑回填/默认配置加载）时，同步初始化校验与控件状态；
// immediate 兜底编辑态页签（render-directive="if"）：面板挂载时 config 已加载完毕，不会再触发整体替换
watch(config, () => {
  setIsIntPutEyesDisabled(config.value?.password_initial?.fixed_password);
  handleMustIncludeRuleChange();
  triggerPasswordConfigValidate();
}, { immediate: true });

defineExpose({
  validate: handleValidate,
});
</script>

<style lang="less" scoped>
@import url('@/components/notify-editor/NotifyEditor.less');

.div-flex {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #63656e;
}

.form-item-flex {
  ::v-deep .bk-form-content {
    display: flex;

    .input-password {
      width: 240px;
      margin-left: 28px;
    }
  }
}

.error-text {
  font-size: 12px;
  line-height: 1;
  color: #ea3636;
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
