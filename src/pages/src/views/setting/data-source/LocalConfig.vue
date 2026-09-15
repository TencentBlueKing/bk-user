<template>
  <bk-loading
    :loading="contentLoading || submitLoading"
    class="data-source-content user-scroll-y"
    :z-index="10"
  >
    <StepLayout :step="step" :steps="steps">
      <template #step-1>
        <bk-form
          class="flex flex-col divide-y divide-[#EAEBF0]"
          ref="formRef"
          :model="formModel"
          :rules="formRules"
          form-type="vertical"
        >
          <DataSourceBasicInfo
            v-model="formModel.name"
          />
          <!-- 冲突配置：编辑态仅回显不可改（后端不支持更新，提交不携带），提示语仅新增展示 -->
          <Row :title="$t('冲突配置')">
            <div class="w-[560px]">
              <ConflictTips
                v-if="!isEdit"
                type="alert"
                :has-other-data-source="hasOtherDataSource"
              />
              <ConflictConfig
                ref="conflictConfigRef"
                :config="conflictConfig"
                :disabled="isEdit"
                class="mt-[16px]"
              />
            </div>
          </Row>
          <Row v-if="!isEdit" :title="$t('导入')">
            <bk-form-item property="uploadFile" class="mb-[24px] w-[560px]">
              <ExcelUpload v-model="formModel.uploadFile" />
            </bk-form-item>
          </Row>
        </bk-form>
      </template>
      <template #step-2>
        <bk-form
          class="flex flex-col divide-y divide-[#EAEBF0]"
          ref="formRef"
          :model="formModel"
          :rules="formRules"
          form-type="vertical"
        >
          <Row :title="$t('密码设置')">
            <bk-form-item :label="$t('启用密码规则')" required>
              <!-- 仅在被本地账密生效范围引用（开关禁用）时展示 tooltip，正常状态不展示 -->
              <bk-switcher
                v-model="enablePassword"
                theme="primary"
                :disabled="isPasswordRuleReferenced"
                v-bk-tooltips="{
                  content: $t('已被本地账密的生效范围引用，无法关闭'),
                  disabled: !isPasswordRuleReferenced,
                  placement: 'right'
                }"
                @change="handleChange"
              />
            </bk-form-item>
          </Row>
          <!-- 密码相关配置（密码规则/初始密码/登录限制/密码有效期）存储于本地数据源 plugin_config，
           取数与提交均走数据源详情接口（getDataSourceDetails / putDataSourceDetails） -->
          <template v-if="enablePassword && formModel.config">
            <Row :title="$t('密码规则')" v-if="formModel.config?.password_rule">
              <bk-form-item :label="$t('密码长度')" property="config.password_rule.min_length" required>
                <bk-input
                  style="width: 200px;"
                  type="number"
                  :suffix="$t('至32位')"
                  :min="10"
                  :max="32"
                  v-model="formModel.config.password_rule.min_length"
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
                    v-model="formModel.config.password_rule.not_continuous_count"
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
            <Row :title="$t('初始密码设置')" v-if="formModel.config?.password_initial">
              <bk-form-item label="" required>
                <div class="div-flex">
                  <bk-checkbox
                    v-model="formModel.config.password_initial.cannot_use_previous_password"
                    @change="handleChange">
                    {{ $t('修改密码时不能重复前') }}
                  </bk-checkbox>
                  <bk-input
                    style="width: 85px;"
                    type="number"
                    behavior="simplicity"
                    :min="0"
                    :max="5"
                    v-model="formModel.config.password_initial.reserved_previous_password_count"
                    @change="handleChange"
                  />
                  <span>{{ $t('次 用过的密码') }}</span>
                </div>
              </bk-form-item>
              <bk-form-item class="form-item-flex" :label="$t('密码生成方式')" required>
                <bk-radio-group v-model="formModel.config.password_initial.generate_method" @change="handleChange">
                  <bk-radio label="random">{{ $t('随机') }}</bk-radio>
                  <bk-radio label="fixed">{{ $t('固定') }}</bk-radio>
                </bk-radio-group>
                <div v-if="formModel.config.password_initial.generate_method === 'fixed'">
                  <passwordInput
                    v-model="formModel.config.password_initial.fixed_password"
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
                :required="formModel.config.password_initial.generate_method === 'random'">
                <NotifyEditorTemplate
                  :active-methods="formModel.config.password_initial.notification.enabled_methods"
                  :checkbox-info="NOTIFICATION_METHODS"
                  :data-list="formModel.config.password_initial.notification.templates"
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
                        v-model="formModel.config.password_initial.notification.enabled_methods"
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
            <Row :title="$t('登录限制')" v-if="formModel.config?.login_limit">
              <bk-form-item label="" required>
                <bk-checkbox
                  v-model="formModel.config.login_limit.force_change_at_first_login"
                  @change="handleChange">
                  {{ $t('首次登录强制修改密码') }}
                </bk-checkbox>
              </bk-form-item>
              <bk-form-item :label="$t('密码试错次数')" required>
                <bk-radio-group v-model="formModel.config.login_limit.max_retries" @change="handleChange">
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
                  v-model="formModel.config.login_limit.lock_time"
                  @change="handleChange"
                />
              </bk-form-item>
            </Row>
            <Row :title="$t('密码有效期设置')" v-if="formModel.config?.password_expire">
              <bk-form-item :label="$t('密码有效期')" required>
                <bk-radio-group v-model="formModel.config.password_expire.valid_time" @change="handleChange">
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
                <bk-checkbox-group
                  v-model="formModel.config.password_expire.remind_before_expire"
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
                property="config.password_expire.notification.enabled_methods"
                required
              >
                <NotifyEditorTemplate
                  :active-methods="formModel.config.password_expire.notification.enabled_methods"
                  :checkbox-info="NOTIFICATION_METHODS"
                  :data-list="formModel.config.password_expire.notification.templates"
                  :is-template="isPasswordExpire"
                  :expiring-email-key="'password_expiring'"
                  :expired-email-key="'password_expired'"
                  :expiring-sms-key="'password_expiring'"
                  :expired-sms-key="'password_expired'"
                  @handle-editor-text="handleEditorText">
                  <template #label>
                    <div class="password-header">
                      <bk-checkbox-group
                        v-model="formModel.config.password_expire.notification.enabled_methods"
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
    </StepLayout>
    <div class="data-source-footer-btn !border-t-0">
      <div>
        <bk-button
          v-if="step === 1"
          theme="primary"
          class="mr8"
          @click="handleNextStep"
        >
          {{ $t('下一步') }}
        </bk-button>
        <template v-else>
          <bk-button
            class="mr-[8px]"
            @click="handlePrevStep"
          >
            {{ $t('上一步') }}
          </bk-button>
          <bk-button
            theme="primary"
            class="mr8"
            :loading="submitLoading"
            @click="handleSubmit"
          >
            {{ isEdit ? $t('保存') : $t('提交') }}
          </bk-button>
        </template>
        <bk-button @click="emit('cancel')">
          {{ $t('取消') }}
        </bk-button>
      </div>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { AngleDown, AngleUp } from 'bkui-vue/lib/icon';
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import StepLayout from './StepLayout.vue';

import { isNil } from '@/common/util';
import ConflictConfig from '@/components/conflict-config/ConflictConfig.vue';
import ConflictTips from '@/components/conflict-config/ConflictTips.vue';
import DataSourceBasicInfo from '@/components/DataSourceBasicInfo.vue';
import { UPLOAD_FILE_MAX_SIZE_BYTE } from '@/components/import-dialog/constants';
import ExcelUpload from '@/components/import-dialog/ExcelUpload.vue';
import Row from '@/components/layouts/ItemRow.vue';
import NotifyEditorTemplate from '@/components/notify-editor/NotifyEditorTemplate.vue';
import passwordInput from '@/components/passwordInput.vue';
import { useValidate } from '@/hooks';
import { useConflictRules } from '@/hooks/useConflictRules';
import { useDataSourceImport } from '@/hooks/useDataSourceImport';
import { getIdps, getLocalIdps, randomPasswords } from '@/http';
import {
  getDataSourceDetails,
  getDefaultConfig,
  newDataSource,
  putDataSourceDetails,
} from '@/http/dataSourceFiles';
import { DataSourceDetails, LocalDataSourcePluginConfig, LocalIdpLoginLimit, LocalIdpPasswordExpire, LocalIdpPasswordInitial, LocalIdpPasswordRule, UsernameGenerateConfig } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';
import { useDataSourceStore } from '@/store';
import { NOTIFICATION_METHODS, passwordMustIncludes, passwordNotAllowed, REMIND_DAYS, VALID_TIME } from '@/utils';

interface Props {
  dataSourceId: number | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  cancel: [];
  updateSuccess: [payload: { text: string; dataSourceId: number; name: string }];
}>();

/** 编辑模式（仅改名称，不展示导入） */
const isEdit = computed(() => !isNil(props.dataSourceId));
/** 编辑模式回填的数据源详情，提交时原样带回，只替换名称 */
const detailData = ref<DataSourceDetails>();

const conflictConfigRef = ref();
const conflictConfig = ref<UsernameGenerateConfig>({
  rule: 'unchanged',
  prefix: '',
  suffix: '',
});
const { rules: conflictRules } = useConflictRules(conflictConfigRef);
const formRef = ref();
// 空通知结构：骨架阶段占位，保证模板中 notification 的绑定路径始终存在
const emptyNotification = (): LocalIdpPasswordInitial['notification'] => ({ enabled_methods: [], templates: [] });

const formModel = ref<{ name?: string; config?: LocalDataSourcePluginConfig; uploadFile?: File | null }>({
  name: '',
  uploadFile: null,
  // 初始化四段空骨架：首帧即渲染完整表单结构，接口数据到位后仅填值，避免分批出现
  config: {
    enable_password: false,
    password_rule: {} as LocalIdpPasswordRule,
    password_initial: { notification: emptyNotification() } as LocalIdpPasswordInitial,
    password_expire: { valid_time: 90, notification: emptyNotification() } as LocalIdpPasswordExpire,
    login_limit: { max_retries: 5 } as LocalIdpLoginLimit,
  },
});
const dataSourceStore = useDataSourceStore();

// 当前步骤由组件自持（校验完成后自行更新），不再经容器转发；
// 支持路由 query.step 直达（生效范围"去设置"提示跳入编辑页密码设置步骤，刷新/直达链接同样生效）。
// 仅编辑态生效：新增态直达会跳过步骤 1 的 name/上传文件校验，造成无导入文件的脏数据源
const route = useRoute();
const step = ref(isEdit.value && Number(route.query.step) === 2 ? 2 : 1);
const steps = [
  { title: t('基础配置') },
  { title: t('密码设置') },
];

const hasOtherDataSource = computed(() => dataSourceStore.dataSource.length > 0);
const { uploadImport } = useDataSourceImport();
const submitLoading = ref(false);
// 编辑模式取数（基础信息 + 密码相关配置）期间的整页 loading
const contentLoading = ref(false);
// 本地账密的生效范围是否已引用当前数据源：引用后不允许关闭密码规则（开关置灰）
const isPasswordRuleReferenced = ref(false);
// 是否启用密码规则：取数据源配置的 enable_password（新增态以 default-config 接口返回为准）；关闭后步骤 2 仅展示提示
const enablePassword = computed({
  get: () => formModel.value.config?.enable_password ?? false,
  set: (value: boolean) => {
    if (formModel.value.config) {
      formModel.value.config.enable_password = value;
    }
  },
});

const validate = useValidate();
const formRules = {
  ...conflictRules,
  // key 需与 form-item 的 property 完整路径一致，否则规则无法命中
  'config.password_rule.min_length': [validate.required],
  uploadFile: [
    { required: true, message: t('请选择文件再上传'), trigger: 'change' },
    {
      validator: (value: File | null) => !value || value.size <= UPLOAD_FILE_MAX_SIZE_BYTE,
      message: t('文件大小超出限制'),
      trigger: 'change',
    },
  ],
};

// ==== 迁移自「设置 > 登录设置 - 本地账密」的密码相关配置逻辑 ====
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

// 初始密码/密码到期的通知模板展开态
const isPasswordInitial = ref(false);
const isDropdownPasswordInitial = ref(false);
const isPasswordExpire = ref(false);
const isDropdownPasswordExpire = ref(false);
const passwordRuleError = ref(false);
const passwordCountError = ref(false);
const passwordConfigError = ref(false);
const enabledMethodsError = ref(false);
const isInputEyesDisabled = ref(false);

const maxTrailTimesList = reactive([
  { times: 3, text: `3 ${t('次')}` },
  { times: 5, text: `5 ${t('次')}` },
  { times: 10, text: `10 ${t('次')}` },
]);

const isContinuousDisabled = computed(() => Number(formModel.value.config?.password_rule?.not_continuous_count) === 0);

const mustIncludeList = computed({
  get: () => {
    const rule = formModel.value.config?.password_rule;
    if (!rule) return [];
    return mustIncludeOptions.filter(opt => rule[opt.label]).map(opt => opt.label);
  },
  set: (value: string[]) => {
    const rule = formModel.value.config?.password_rule;
    if (!rule) return;
    mustIncludeOptions.forEach((opt) => {
      rule[opt.label] = value.includes(opt.label);
    });
  },
});

// bk-checkbox-group 绑定数组与接口布尔字段的转换
const continuousRuleList = computed({
  get: () => {
    const rule = formModel.value.config?.password_rule;
    if (!rule) return [];
    return continuousOptions.filter(opt => rule[opt.label]).map(opt => opt.label);
  },
  set: (value: string[]) => {
    const rule = formModel.value.config?.password_rule;
    if (!rule) return;
    continuousOptions.forEach((opt) => {
      rule[opt.label] = value.includes(opt.label);
    });
  },
});

/** 步骤 1 → 步骤 2：基础信息与导入文件（uploadFile）均走 form-item 校验 */
const handleNextStep = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;
  // 切步后第一步随 v-if 卸载，而提交发生在第二步，故在此同步冲突配置，避免 getData() 取不到导致参数缺失
  conflictConfig.value = conflictConfigRef.value?.getData() ?? conflictConfig.value;
  step.value = 2;
};

const handlePrevStep = () => {
  step.value = 1;
};

const handleChange = () => {
  window.changeInput = true;
};

// 编辑通知方式
const handleEditorText = (html: string, text: string, key: string, type: string) => {
  const templates = key === 'password_expiring' || key === 'password_expired'
    ? formModel.value.config?.password_expire?.notification?.templates ?? []
    : formModel.value.config?.password_initial?.notification?.templates ?? [];
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
    const params = { password_rule_config: formModel.value.config?.password_rule };
    const passwordRes = await randomPasswords(params);
    formModel.value.config.password_initial.fixed_password = passwordRes.data.password;
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
  formModel.value.config.password_initial.fixed_password = val;
};

/** 密码不能连续出现的次数 */
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

/** 密码规则 */
const triggerPasswordConfigValidate = () => {
  // 未启用密码规则时跳过校验
  if (!enablePassword.value) return;
  const enabledRules = Object.entries(formModel.value.config?.password_rule ?? {})
    .filter(([key, val]) => passwordNotAllowed[key as keyof typeof passwordNotAllowed] && val);
  // 密码不能连续出现的次数不为0时，必须选择至少一个密码不能连续出现的规则
  if (formModel.value.config?.password_rule?.not_continuous_count !== 0) {
    passwordConfigError.value = enabledRules.length === 0;
  }
};
/** 密码必须包含规则校验 */
const handleMustIncludeRuleChange = () => {
  if (!enablePassword.value) return;
  const list = Object.entries(formModel.value.config?.password_rule ?? {})
    .filter(([key, val]) => passwordMustIncludes[key as keyof typeof passwordMustIncludes] && val);
  passwordRuleError.value = !list.some(([, val]) => val);
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

const handleSubmit = async () => {
  try {
    const valid = await formRef.value?.validate().catch(() => false);
    if (!valid) return;
    // 密码相关的组合校验跨多个字段，不在 formRules 内，需单独拦截，避免只显示红字却放行提交
    if (!validatePasswordConfig()) return;
    // 编辑模式：名称与密码相关配置（plugin_config）一并提交，字段映射原样保留
    if (isEdit.value) {
      submitLoading.value = true;
      await putDataSourceDetails(props.dataSourceId, {
        name: formModel.value.name,
        plugin_config: formModel.value.config,
        field_mapping: detailData.value.field_mapping,
      });
      window.changeInput = false;
      emit('updateSuccess', {
        text: t('更新'),
        dataSourceId: props.dataSourceId,
        name: formModel.value.name,
      });
      return;
    }
    // 新增模式：创建数据源并导入（文件已在步骤 1 通过 form-item 校验，此处不再重复校验）
    submitLoading.value = true;
    const result = await newDataSource({
      plugin_id: 'local',
      name: formModel.value.name,
      plugin_config: formModel.value.config,
      username_generate_config: conflictConfig.value,
    });

    const dataSourceId = result.data?.id;
    if (!dataSourceId) {
      Message({ theme: 'error', message: t('创建数据源失败') });
      return;
    }

    await uploadImport(dataSourceId, formModel.value.uploadFile!);
    window.changeInput = false;
    emit('updateSuccess', {
      text: t('新建成功'),
      dataSourceId,
      name: formModel.value.name,
    });
  } catch (e) {
    console.error(e);
    // 透传后端错误信息（如名称重复等），避免统一提示掩盖具体原因
    const errorMessage = (e as { response?: { data?: { error?: { message?: string } } } })
      ?.response?.data?.error?.message;
    Message({ theme: 'error', message: errorMessage || t('操作失败') });
  } finally {
    submitLoading.value = false;
  }
};

/** 初始化表单：编辑模式回填数据源详情，新增模式以插件默认配置初始化 */
const initForm = async () => {
  contentLoading.value = true;
  try {
    if (isEdit.value) {
      const detailsRes = await getDataSourceDetails(props.dataSourceId);
      const details = detailsRes?.data;
      formModel.value.name = details?.name ?? '';
      detailData.value = details;
      // 冲突配置回填：编辑态仅回显（提交不携带该字段），无数据时兜底为不配置
      conflictConfig.value = details?.username_generate_config
        || { rule: 'unchanged', prefix: '', suffix: '' };
      // 密码相关配置取数：已迁移至数据源详情的 plugin_config（存量数据由后端迁移），为空时保留骨架默认值
      if (details?.plugin_config && Object.keys(details.plugin_config).length > 0) {
        formModel.value.config = details.plugin_config as LocalDataSourcePluginConfig;
      }
      // 生效范围仍在本地账密（认证源）上，据此判断密码规则是否已被引用
      const idpsRes = await getIdps('');
      const localIdp = idpsRes?.data?.find(item => item.plugin?.id === 'local');
      if (localIdp) {
        const idpDetailRes = await getLocalIdps(localIdp.id);
        const scopeIds = idpDetailRes?.data?.data_source_ids ?? [];
        isPasswordRuleReferenced.value = scopeIds.includes(props.dataSourceId);
      }
    } else {
      // 新增模式：以插件默认配置初始化表单，用户修改后原样提交
      const res = await getDefaultConfig('local');
      formModel.value.config = res?.data?.config as LocalDataSourcePluginConfig;
    }
    setIsIntPutEyesDisabled(formModel.value.config?.password_initial?.fixed_password);
    handleMustIncludeRuleChange();
    triggerPasswordConfigValidate();
  } catch (e) {
    console.error(e);
  } finally {
    contentLoading.value = false;
  }
};

// 监听密码生成方式
watch(() => formModel.value.config?.password_initial?.generate_method, (value) => {
  enabledMethodsError.value = value === 'random'
    && !(formModel.value.config?.password_initial?.notification?.enabled_methods ?? []).length;
  if (value === 'random') {
    formModel.value.config.password_initial.fixed_password = null;
  }
});

watch(() => formModel.value.config?.password_initial?.notification?.enabled_methods, (value) => {
  if (formModel.value.config?.password_initial?.generate_method === 'fixed') {
    return enabledMethodsError.value = false;
  }
  enabledMethodsError.value = !(value ?? []).length;
});

onMounted(initForm);
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
