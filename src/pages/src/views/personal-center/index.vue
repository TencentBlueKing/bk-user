<template>
  <bk-resize-layout
    class="personal-center-wrapper"
    immediate
    :min="320"
    :max="500"
    :initial-divide="320"
    v-bkloading="{ loading: isLoading }"
  >
    <template #aside>
      <div class="personal-center-left">
        <div class="left-natural-user">
          <div class="natural-user">
            <i class="bk-sq-icon icon-personal-user" />
            <bk-overflow-title type="tips" class="name">
              {{ currentNaturalUser.full_name }}
            </bk-overflow-title>
            <bk-overflow-title type="tips" class="id">
              （{{ currentUserInfo.id }}）
            </bk-overflow-title>
            <!-- <i class="user-icon icon-edit" /> -->
          </div>
        </div>
        <div class="left-add">
          <p>
            <span class="account">{{ $t('已关联账号') }}</span>
            <span class="number">{{ currentNaturalUser.tenant_users?.length }}</span>
          </p>
          <!-- <bk-button theme="primary" text>
            <i class="user-icon icon-add-2 mr8" />
            新增关联
          </bk-button> -->
        </div>
        <ul class="left-list">
          <li
            v-for="(item, index) in currentNaturalUser.tenant_users"
            :key="index"
            :class="{ isActive: currentUserInfo.id === item.id }"
            @click="handleClickItem(item)"
          >
            <div class="account-item">
              <div class="w-4/5">
                <img v-if="item.logo" :src="item.logo" />
                <i v-else class="user-icon icon-yonghu" />
                <span class="name text-overflow" v-bk-tooltips="{ content: item.full_name }">{{ item.full_name }}</span>
                <span
                  class="tenant text-overflow"
                  v-bk-tooltips="{ content: `@ ${item.tenant.name}（${item.tenant.id}）` }"
                >
                  {{ `@ ${item.tenant.name}（${item.tenant.id}）` }}
                </span>
              </div>
              <bk-tag type="filled" theme="success" v-if="userInfo.username === item.id">
                {{ $t('当前登录') }}
              </bk-tag>
            </div>
          </li>
        </ul>
      </div>
    </template>
    <template #main>
      <div class="personal-center-main" v-bkloading="{ loading: infoLoading }">
        <header>
          <div class="header-left">
            <bk-upload
              :ext-cls="currentUserInfo.logo ? 'show-logo' : 'normal-logo'"
              theme="picture"
              with-credentials
              :multiple="false"
              :files="files"
              :handle-res-code="handleRes"
              :url="currentUserInfo.logo"
              :custom-request="customRequest"
              :size="2"
              @error="handleError"
              v-bk-tooltips="{ content: t('支持 jpg、png，尺寸不大于 1024px*1024px，不大于 256KB'), theme: 'light' }"
            >
              <template #trigger>
                <div class="logo-box" v-if="currentUserInfo.logo">
                  <img :src="currentUserInfo.logo" />
                  <div class="logo-hover">
                    <i class="user-icon icon-edit" @click="customRequest" />
                  </div>
                </div>
                <i v-else class="user-icon icon-yonghu" />
              </template>
            </bk-upload>
            <div>
              <div class="user-info">
                <span class="name">{{ currentTenantInfo.username }}</span>
                <div>
                  <span class="span-logo">T</span>
                  {{ currentTenantInfo.tenant?.id }}
                </div>
              </div>
              <p class="login-time">{{ $t('最近登录时间') }}：{{ '--' }}</p>
            </div>
          </div>
          <div class="header-right">
            <span
              v-bk-tooltips="{
                content: $t('当前用户不支持修改密码'),
                distance: 20,
                disabled: canChangePassword,
              }">
              <bk-button
                class="min-w-[88px]"
                :disabled="!canChangePassword"
                @click="showPasswordModal">
                {{ $t('修改密码') }}
              </bk-button>
            </span>
            <span
              v-bk-tooltips="{
                content: $t('该账号已登录'),
                distance: 20,
                disabled: !isCurrentTenant,
              }">
              <bk-button :disabled="isCurrentTenant">
                {{ $t('切换为该账号登录') }}
              </bk-button>
            </span>
            <!-- <bk-button>
              取消关联
            </bk-button> -->
          </div>
        </header>
        <div class="personal-center-details">
          <ul class="details-info">
            <li class="details-info-item">
              <div class="item-header">
                <p class="item-title">{{ $t('身份信息') }}</p>
              </div>
              <bk-form
                ref="formRef"
                class="item-content"
                :model="currentUserInfo"
                :rules="rules">
                <div class="item-div">
                  <li>
                    <span class="key">{{ $t('用户名') }}：</span>
                    <span class="value">{{ currentUserInfo.username }}</span>
                  </li>
                  <li>
                    <span class="key">{{ $t('姓名') }}：</span>
                    <span class="value">{{ currentUserInfo.full_name }}</span>
                  </li>
                  <li>
                    <span class="key">
                      <span class="required-icon"> * </span>
                      {{ $t('邮箱') }}：</span>
                    <div class="value-content">
                      <div>
                        <bk-tag :theme="tagTheme(currentUserInfo.is_inherited_email)">
                          {{ tagText(currentUserInfo.is_inherited_email) }}
                        </bk-tag>
                        <span class="value">
                          {{ currentUserInfo.is_inherited_email
                            ? currentUserInfo.email
                            : currentUserInfo.custom_email }}
                        </span>
                        <i
                          class="user-icon icon-edit"
                          @click="verifyIdentityInfo(OpenDialogMode.Edit, OpenDialogType.email)">
                        </i>

                        <i class="ml-[10px] user-icon icon-remind-fill text-[#FF9C01]"></i>
                        <bk-button
                          text
                          theme="primary"
                          @click="verifyIdentityInfo(OpenDialogMode.Verify, OpenDialogType.email)">
                          验证
                        </bk-button>
                      </div>
                    </div>
                  </li>
                  <li class="mb-[10px]">
                    <span class="key">
                      <span class="required-icon"> * </span>
                      {{ $t('手机号') }}：</span>
                    <div class="value-content">
                      <div>
                        <bk-tag :theme="tagTheme(currentUserInfo.is_inherited_phone)">
                          {{ tagText(currentUserInfo.is_inherited_phone) }}
                        </bk-tag>
                        <span class="value">
                          {{ currentUserInfo.is_inherited_phone
                            ? currentUserInfo.phone
                            : currentUserInfo.custom_phone }}
                        </span>
                        <i
                          class="user-icon icon-edit"
                          @click="verifyIdentityInfo(OpenDialogMode.Edit, OpenDialogType.phone)">
                        </i>

                        <i class="ml-[10px] user-icon icon-remind-fill text-[#FF9C01]"></i>
                        <bk-button
                          text
                          theme="primary"
                          @click="verifyIdentityInfo(OpenDialogMode.Verify, OpenDialogType.phone)">
                          验证
                        </bk-button>
                      </div>
                    </div>
                  </li>
                </div>
                <div class="item-div">
                  <li>
                    <span class="key">{{ $t('所属租户') }}：</span>
                    <span class="value">
                      {{ `${currentTenantInfo.tenant?.name }（${currentTenantInfo.tenant?.id}）`}}
                    </span>
                  </li>
                  <li>
                    <span class="key">{{ $t('所属组织') }}：</span>
                    <span class="value">{{ formatConvert(currentUserInfo.departments) }}</span>
                  </li>
                  <li>
                    <span class="key">{{ $t('直属上级') }}：</span>
                    <span class="value">{{ formatConvert(currentUserInfo.leaders) }}</span>
                  </li>
                </div>
              </bk-form>
              <!-- 自定义字段 -->
              <div class="item-flex">
                <li
                  v-for="(item, index) in currentUserInfo.extras"
                  :key="index"
                >
                  <bk-overflow-title class="key" type="tips">
                    <span v-show="item.required" class="required-icon"> * </span>
                    {{ item.display_name }}：</bk-overflow-title>
                  <div class="value-edit custom-input">
                    <bk-overflow-title v-if="!item.isEdit" class="value" type="tips">
                      {{ customFieldsMap(item) }}
                    </bk-overflow-title>
                    <div v-else class="input-list w-[240px]">
                      <bk-input
                        v-if="item.data_type === 'string'"
                        :class="{ 'custom-error': item.error && !item.value }"
                        v-model="item.value"
                        :maxlength="64"
                        @blur="customBlur(item)"
                        @input="handleInput(item)"
                      />
                      <bk-input
                        v-else-if="item.data_type === 'number'"
                        :class="{ 'custom-error': item.error && !item.value }"
                        type="number"
                        v-model="item.value"
                        :max="4294967296"
                        :min="0"
                        @blur="customBlur(item)"
                        @change="handleInput(item)"
                      />
                      <bk-select
                        v-else
                        :class="{ 'custom-select': item.error && (item.value === '' || !item.value.length) }"
                        v-model="item.value"
                        :clearable="item.data_type === 'multi_enum'"
                        :multiple="item.data_type === 'multi_enum'"
                        @blur="customBlur(item)"
                        @change="changeSelect(item, index)"
                        @clear="clearSelect(item)">
                        <bk-option
                          v-for="(option, i) in item.options"
                          :key="i"
                          :id="option.id"
                          :name="option.value">
                        </bk-option>
                      </bk-select>
                      <span class="error-text" v-show="item.error && (!item.value || !item.value.length)">
                        {{ $t('必填项') }}
                      </span>
                    </div>
                    <i
                      v-if="item.editable && !item.isEdit"
                      class="user-icon icon-edit"
                      @click="editExtra(item, index)" />
                    <div v-if="item.isEdit" style="line-height: 32px;">
                      <bk-button text theme="primary" class="ml-[12px] mr-[12px]" @click="changeCustomFields(item)">
                        {{ $t('确定') }}
                      </bk-button>
                      <bk-button text theme="primary" @click="cancelCustomFields(item, index)">
                        {{ $t('取消') }}
                      </bk-button>
                    </div>
                  </div>
                </li>
              </div>
            </li>
          </ul>
        </div>
        <div class="personal-center-details">
          <ul class="details-info">
            <li class="details-info-item">
              <div class="item-header">
                <p class="item-title">{{ $t('语言和时区') }}</p>
              </div>
              <bk-form
                ref="formRef"
                class="item-content"
                :model="currentUserInfo">
                <div class="item-div" v-for="(item, key) in LanguageAndTimeZone" :key="key">
                  <li>
                    <span class="key">{{ $t(item.label) }}：</span>
                    <div class="value-content">
                      <div class="value-edit" v-if="item.isEdit">
                        <bk-form-item>
                          <bk-select
                            v-model="currentUserInfo[item.model]"
                            clearable
                            :input-search="item.model === 'language'">
                            <bk-option
                              v-for="option in item.options"
                              :key="option.value"
                              :id="option.value"
                              :name="option.label">
                            </bk-option>
                          </bk-select>
                        </bk-form-item>
                        <bk-button text theme="primary" class="ml-[12px] mr-[12px]" @click="item.submitChange(item)">
                          {{ $t('确定') }}
                        </bk-button>
                        <bk-button text theme="primary" @click="item.cancel(item)">{{ $t('取消') }}</bk-button>
                      </div>
                      <div v-else>
                        <span class="value">
                          {{ item.model === 'language' ?
                            showLanguage(currentUserInfo[item.model]) : currentUserInfo[item.model]}}
                        </span>
                        <i class="user-icon icon-edit" @click="item.isEdit = true" />
                      </div>
                    </div>
                  </li>
                </div>
              </bk-form>
            </li>
          </ul>
        </div>
      </div>
      <!-- 修改密码 -->
      <ChangePassword
        :config="passwordModalConfig"
        @closed="hidePasswordModal" />
      <!-- 邮箱、手机号编辑验证 -->
      <verifyIdentityInfoDialog
        v-model:is-show="showVerifyDialog"
        :mode="currentVerifyConfig.mode"
        :type="currentVerifyConfig.type"
        :header-tips="unSupportEidtEmail ? t('继承数据源邮箱不支持编辑，已为您切换为自定义模式进行编辑') : ''"
        v-model:active="currentVerifyConfig.active">
        <template #[OpenDialogActive.inherit]>
          <bk-form :model="editForm" ref="eidtFormRef">
            <div class="m-[10px] mt-[20px] h-[40px]" v-if="currentVerifyConfig.type === OpenDialogType.email">
              <img :src="emailImg" class="verify-icon" />
              <span>
                {{ `${t('请输入')} ${'132465798@qq.com'} ${'收到的邮箱验证码'}` }}
              </span>
            </div>

            <div class="m-[10px] mt-[20px] h-[40px]" v-if="currentVerifyConfig.type === OpenDialogType.phone">
              <img :src="phoneImg" class="verify-icon" />
              <span>
                {{ `${t('请输入')} ${'132465798'} ${'收到的手机验证码'}` }}
              </span>
            </div>

            <div class="flex justify-center m-[10px]">
              <bk-input
                :placeholder="t('请输入验证码')"
                v-model="editForm.captcha"
                :disabled="unSupportEidtEmail" />
              <bk-button outline theme="primary" class="ml-[10px]" :disabled="unSupportEidtEmail">
                {{ t('获取验证码') }}
              </bk-button>
            </div>
          </bk-form>
        </template>
        <template #[OpenDialogActive.custom]>
          <bk-form :model="verifyForm" ref="verifyFormRef">
            <div class="m-[10px] mt-[20px] h-[40px]" v-if="currentVerifyConfig.type === OpenDialogType.email">
              <bk-input :placeholder="t('请输入邮箱以接收邮箱验证码')" v-model="verifyForm.email">
                <template #prefix>
                  <span class="input-icon flex items-center">
                    <img :src="emailImg" class="verify-icon ml-[5px]" />
                  </span>
                </template>
              </bk-input>
            </div>

            <div class="m-[10px] mt-[20px] h-[40px]" v-if="currentVerifyConfig.type === OpenDialogType.phone">
              <bk-input :placeholder="t('请输入手机号以接收短信验证码')" v-model="verifyForm.phone">
                <template #prefix>
                  <span class="input-icon flex items-center">
                    <img :src="phoneImg" class="verify-icon ml-[5px]" />
                  </span>
                </template>
              </bk-input>
            </div>

            <div class="flex justify-center m-[10px]">
              <bk-input :placeholder="t('请输入验证码')" v-model="verifyForm.captcha"></bk-input>
              <bk-button outline theme="primary" class="ml-[10px]">{{ t('获取验证码') }}</bk-button>
            </div>
          </bk-form>
        </template>
        <template #footer>
          <div class="pb-[20px] m-[10px] mb-[0px]">
            <bk-button class="w-[100%] mb-[10px] block" theme="primary" size="large" width="100%"
                       :disabled="unSupportEidtEmail && currentVerifyConfig.active === OpenDialogActive.inherit"
                       @click="handleSubmitVerifyForm">
              {{ t('确定') }}
            </bk-button>
            <bk-button class="w-[100%]" size="large" @click="handleCloseVerifyDialog">{{ t('取消') }}</bk-button>
          </div>
        </template>
      </verifyIdentityInfoDialog>
    </template>
  </bk-resize-layout>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, Message } from 'bkui-vue';
import { computed, inject, nextTick, onMounted, reactive, ref, watch } from 'vue';

import { OpenDialogActive, OpenDialogMode, OpenDialogType } from './openDialogType';
import verifyIdentityInfoDialog from './verifyIdentityInfoDialog.vue';

import ChangePassword from '@/components/ChangePassword.vue';
import { useCustomFields, useValidate } from '@/hooks';
import {
  getCurrentNaturalUser,
  getPersonalCenterUserFeature,
  getPersonalCenterUsers,
  getPersonalCenterUserVisibleFields,
  patchTenantUsersLogo,
  putPersonalCenterUserExtrasFields,
  putUserLanguage,
  putUserTimeZone,
} from '@/http';
import emailImg from '@/images/email.svg';
import phoneImg from '@/images/phone.svg';
import { t } from '@/language/index';
import { useUser } from '@/store/user';
import { customFieldsMap, formatConvert, getBase64, handleSwitchLocale, LANGUAGE_OPTIONS, TIME_ZONES } from '@/utils';

const user = useUser();
const userInfo = ref(user.user);

const validate = useValidate();
const editLeaveBefore = inject('editLeaveBefore');
const currentNaturalUser = ref({});
// 当前用户信息
const currentUserInfo = ref({});
// 当前租户信息
const currentTenantInfo = ref({});

const isLoading = ref(false);
const infoLoading = ref(false);
const isInheritedEmail = ref(true);
const isInheritedPhone = ref(true);
const customEmail = ref('');
const customPhone = ref('');
const customPhoneCode = ref('');
const originalValue = ref({});
const rules = {
  custom_email: [validate.required, validate.email],
};
const formRef = ref();
// 保存修改后的extras数据
const extrasList = ref([]);
// 是否可以修改密码
const canChangePassword = ref(false);

onMounted(() => {
  getNaturalUser();
});

const getNaturalUser = () => {
  isLoading.value = true;
  // 关联账户列表
  getCurrentNaturalUser().then((res) => {
    currentNaturalUser.value = res.data;
    isLoading.value = false;
    getCurrentUser(currentNaturalUser.value.tenant_users[0].id);
  });
};

const getCurrentUser = async (id) => {
  try {
    infoLoading.value = true;
    currentNaturalUser.value?.tenant_users.forEach((item) => {
      if (item.id === id) {
        currentTenantInfo.value = item;
      }
    });
    // 关联账户详情
    const [userRes, featureRes, fieldsRes] = await Promise.all([
      getPersonalCenterUsers(id),
      getPersonalCenterUserFeature(id),
      getPersonalCenterUserVisibleFields(id),
    ]);

    currentUserInfo.value = {
      ...userRes.data,
      extras: useCustomFields(userRes.data?.extras, fieldsRes.data.custom_fields),
    };
    canChangePassword.value = featureRes.data.can_change_password;
    extrasList.value = [...currentUserInfo.value.extras];
    customEmail.value = userRes.data.custom_email;
    customPhone.value = userRes.data.custom_phone;
    customPhoneCode.value = userRes.data.custom_phone_country_code;
    isInheritedEmail.value = currentUserInfo.value.is_inherited_email;
    isInheritedPhone.value = currentUserInfo.value.is_inherited_phone;
    originalValue.value = {
      language: currentUserInfo.value.language,
      time_zone: currentUserInfo.value.time_zone,
    };
  } catch (error) {
    console.warn(error);
  } finally {
    infoLoading.value = false;
  }
};

// 获取当前编辑框焦点
const editExtra = (item, index) => {
  item.isEdit = true;
  if (item.data_type === 'multi_enum' && item.value === '') {
    item.value = [];
  }
  nextTick(() => {
    const customInput = document.getElementsByClassName('custom-input')[index];
    const inputElement = customInput.getElementsByTagName('input')?.[0];
    if (inputElement) {
      inputElement.addEventListener('blur', () => {
        customBlur(item);
      });
      inputElement.focus();
    }
  });
};
// 失焦校验
const customBlur = (item) => {
  item.error = item.value === '' || (item.data_type === 'multi_enum' && !item.value.length);
};

const handleInput = (item) => {
  item.error = false;
};
// 改变枚举值
const changeSelect = (item) => {
  item.value = item.value;
  item.error = false;
};

const clearSelect = (item) => {
  item.error = true;
};
// 提交修改自定义字段
const changeCustomFields = async (item) => {
  try {
    if (item.error) {
      return;
    }
    const params = {
      id: currentUserInfo.value.id,
      extras: {
        [item.name]: item.value,
      },
    };
    await putPersonalCenterUserExtrasFields(params);
    extrasList.value = JSON.parse(JSON.stringify(currentUserInfo.value.extras));
    item.isEdit = false;
    Message({ theme: 'success', message: t('保存成功') });
  } catch (error) {
    console.warn(error);
  }
};

const showLanguage = computed(() => (targetValue) => {
  const foundItem = LANGUAGE_OPTIONS?.find(item => item.value === targetValue);
  return foundItem ? foundItem.label : null;
});

const submitChange  = async (item) => {
  const { model } = item;
  try {
    if (!currentUserInfo.value[model]) return;
    const apiCall = model === 'language' ? putUserLanguage : putUserTimeZone;
    await apiCall({
      id: currentUserInfo.value.id,
      [model]: currentUserInfo.value[model],
    });

    item.isEdit = false;
    Message({ theme: 'success', message: t('保存成功') });
    if (model === 'language') {
      setTimeout(() => handleSwitchLocale(currentUserInfo.value.language), 100);
    }
    originalValue.value[model] = currentUserInfo.value[model];
  } catch (error) {
    console.warn(error);
  }
};

const cancelChange = (item) => {
  item.isEdit = false;
  currentUserInfo.value[item.model] = originalValue.value[item.model];
};

const LanguageAndTimeZone = ref({
  language: {
    label: t('语言'),
    isEdit: false,
    model: 'language',
    options: LANGUAGE_OPTIONS,
    submitChange,
    cancel: cancelChange,
  },
  timeZone: {
    label: t('时区'),
    isEdit: false,
    model: 'time_zone',
    options: TIME_ZONES,
    submitChange,
    cancel: cancelChange,
  },
});

// 取消自定义字段修改
const cancelCustomFields = (item, index) => {
  item.value = extrasList.value[index]?.value;
  item.isEdit = false;
  item.error = false;
};

watch(() => currentUserInfo.value?.extras, (val) => {
  if (val.length) {
    const allFalse = val.every(item => !item.isEdit);
    window.changeInput = !(allFalse && isEditEmail.value === false && isEditPhone.value === false);
  }
}, {
  deep: true,
});

const tagTheme = value => (value ? 'info' : 'warning');
const tagText = value => (value ? t('继承数据源') : t('自定义'));

const isCurrentTenant = computed(() => currentNaturalUser.value.full_name === currentTenantInfo.value.full_name);

const isEditPhone = ref(false);

watch(() => isEditPhone.value, (val) => {
  if (val) {
    window.changeInput = true;
  }
});

const showVerifyDialog = ref(false);
const currentVerifyConfig = reactive({
  mode: OpenDialogMode.Verify,
  type: OpenDialogType.email,
  active: null,
});

interface EidtForm {
  captcha: string,
}
const editForm = reactive<EidtForm>({
  captcha: '',
});
const resetEditForm = () => {
  editForm.captcha = '';
};

const eidtFormRef = ref(null);

interface VerifyForm {
  email: string,
  phone: string,
  captcha: string,
}
const verifyForm = reactive<VerifyForm>({
  email: '',
  phone: '',
  captcha: ''
});
const resetVerifyForm = () => {
  verifyForm.email = '';
  verifyForm.phone = '';
  verifyForm.captcha = '';
};

const verifyFormRef = ref(null);

const unSupportEidtEmail = computed(() =>
currentVerifyConfig.type === OpenDialogType.email
&& currentVerifyConfig.mode === OpenDialogMode.Edit);

// 验证身份信息下的邮箱或手机号
const verifyIdentityInfo = (mode: OpenDialogMode, type: OpenDialogType) => {
  currentVerifyConfig.mode = mode;
  currentVerifyConfig.type = type;
  const { inherit, custom } = OpenDialogActive;
  // 根据当前tag来决定打开dialog面板的active
  if (type === OpenDialogType.email && mode === OpenDialogMode.Verify) {
    currentVerifyConfig.active = currentUserInfo.value.is_inherited_email ? inherit : custom;
  }
  // 邮箱不支持继承 只能自定义
  if (type === OpenDialogType.email && mode === OpenDialogMode.Edit) {
    currentVerifyConfig.active = custom;
  }
  if (type === OpenDialogType.phone) {
    currentVerifyConfig.active = currentUserInfo.value.is_inherited_phone ? inherit : custom;
  }
  showVerifyDialog.value = true;
};

const handleCloseVerifyDialog = () => {
  showVerifyDialog.value = false;
  resetEditForm();
  resetVerifyForm();
};

const handleSubmitVerifyForm = () => {
  console.log(verifyForm);
  console.log(editForm);
  handleCloseVerifyDialog();
};

// 切换关联账号
const handleClickItem = async (item: any) => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
  getCurrentUser(item.id);
};

const handleRes = (response: any) => {
  if (response.id) {
    return true;
  }
  return false;
};

const customRequest = (event) => {
  getBase64(event.file).then((res) => {
    currentUserInfo.value.logo = res;
    patchTenantUsersLogo({
      id: currentUserInfo.value.id,
      logo: currentUserInfo.value.logo,
    });
  })
    .catch((e) => {
      console.warn(e);
    });
};

const handleError = (file) => {
  if (file.size > (2 * 1024 * 1024)) {
    Message({ theme: 'error', message: t('图片大小超出限制，请重新上传') });
  }
};

// 修改密码
const passwordModalConfig = ref({
  isShow: false,
  title: t('修改密码'),
  id: '',
});

const showPasswordModal = () => {
  passwordModalConfig.value.isShow = true;
  passwordModalConfig.value.id = currentUserInfo.value?.id;
};

const hidePasswordModal = () => {
  passwordModalConfig.value.isShow = false;
};
</script>

<style lang="less" scoped>
.personal-center-wrapper {
  height: calc(100vh - 52px);
  min-width: 1600px;

  .personal-center-left {
    height: 100%;
    background-color: #fff;

    .left-natural-user {
      padding: 16px;

      .natural-user {
        display: flex;
        height: 40px;
        padding: 0 10px;
        line-height: 40px;
        background: #F0F1F5;
        border-radius: 2px;
        align-items: center;

        i {
          font-size: 16px;
          color: #979BA5;
        }

        .name {
          max-width: 120px;
          margin-left: 8px;
          font-size: 14px;
          font-weight: 700;
        }

        .id {
          min-width: 120px;
          color: #979BA5;
        }
      }
    }

    .left-add {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 16px 16px;

      .account {
        margin-right: 8px;
        font-size: 14px;
      }

      .number {
        display: inline-block;
        height: 16px;
        padding: 0 8px;
        line-height: 16px;
        color: #979ba5;
        text-align: center;
        background: #f0f1f5;
        border-radius: 8px;
      }

      .bk-button {
        font-size: 14px;
      }
    }

    .left-list {
      li {
        padding: 0 12px 0 24px;

        &:hover {
          background: #f0f1f5;
        }

        .account-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          height: 40px;
          line-height: 40px;
          cursor: pointer;

          div {
            display: flex;
            align-items: center;
          }

          img {
            display: inline-block;
            width: 22px;
            height: 22px;
            vertical-align: middle;
            object-fit: contain;
          }

          .icon-yonghu {
            padding: 3px;
            font-size: 16px;
            color: #FAFBFD;
            background: #DCDEE5;
            border-radius: 2px;
          }

          .name {
            display: inline-block;
            margin: 0 8px;
            font-size: 14px;
            color: #313238;
          }

          .tenant {
            display: inline-block;
            color: #ff9c01;
          }
        }
      }

      .isActive {
        background-color: #e1ecff;

        &:hover {
          background-color: #e1ecff;
        }
      }
    }
  }

  .personal-center-main {
    padding: 24px;

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .header-left {
        display: flex;

        ::v-deep .normal-logo {
          .bk-upload-trigger--picture {
            width: 72px;
            height: 72px;
            margin: 0;
            margin-right: 16px;

            .icon-yonghu {
              width: 72px;
              height: 72px;
              margin-right: 0;
              font-size: 40px;
              line-height: 72px;
              color: #DCDEE5;
              background: #FAFBFD;

              &:hover {
                color: #A3C5FD;
                cursor: pointer;
                background: #F0F1F5;
              }
            }
          }

          // .bk-upload-trigger--has-file {
          //   border-style: dashed;
          // }

          // .bk-upload-trigger--fail {
          //   border-color: #c4c6cc;

          //   &:hover {
          //     border-color: #3A84FF;
          //   }
          // }
        }

        ::v-deep .show-logo {
          .bk-upload-trigger--picture {
            position: relative;
            width: 72px;
            height: 72px;
            margin: 0;
            margin-right: 16px;
            border-style: solid;

            &:hover {
              border-color: #c4c6cc;
            }

            .logo-box {
              padding: 2px;

              img {
                object-fit: contain;
                width: 66px;
                height: 66px;
              }

              &:hover {
                .logo-hover {
                  display: block;
                }
              }

              .logo-hover {
                position: absolute;
                top: 2px;
                left: 2px;
                z-index: 9;
                display: none;
                width: 66px;
                height: 66px;
                line-height: 66px;
                color: #fff;
                text-align: center;
                background-color: rgb(0 0 0 / 60%);
                border: 1px solid #ff5656;

                i {
                  font-size: 16px;
                }
              }
            }
          }
        }

        .user-info {
          display: flex;
          font-size: 32px;
          font-weight: 700;
          align-items: center;

          div {
            height: 24px;
            padding-right: 8px;
            margin-left: 16px;
            font-size: 12px;
            font-weight: 400;
            line-height: 24px;
            background: #EAEBF0;
            border-radius: 2px;

            .span-logo {
              margin-right: 0;
              margin-left: 4px;
              background: #3A84FF;
            }
          }
        }

        .login-time {
          font-size: 14px;
        }
      }
    }

    .personal-center-details {
      // height: calc(100vh - 196px);
      margin-top: 24px;

      .details-info {
        .details-info-item {
          padding: 16px 24px;
          margin-bottom: 16px;
          background: #fff;
          border-radius: 2px;
          box-shadow: 0 2px 4px 0 #1919290d;

          .item-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
          }

          .item-title {
            font-size: 14px;
            font-weight: 700;
          }

          .item-content {
            display: flex;
            margin-top: 16px;

            .item-div {
              width: 50%;
              min-width: 600px;

              li {
                display: flex;
                width: 100%;
                min-width: 600px;
                font-size: 14px;
                line-height: 50px;

                .key {
                  display: inline-block;
                  width: 120px;
                  text-align: right;
                }

                .value {
                  max-width: 500px;
                  overflow: hidden;
                  color: #313238;
                  text-overflow: ellipsis;
                  white-space: nowrap;
                }

                .value-content {
                  .value-edit {
                    display: flex;
                    align-items: center;
                    height: 50px;

                    .bk-input {
                      width: 240px;
                    }
                  }

                  .icon-edit {
                    margin-left: 10px;
                    font-size: 16px;
                    color: #979BA5;
                    cursor: pointer;

                    &:hover {
                      color: #3A84FF;
                    }
                  }

                  ::v-deep .bk-form-item {
                    margin-bottom: 0;

                    .bk-form-content {
                      margin-left: 0 !important;
                    }
                  }
                }
              }
            }
          }

          .item-flex {
            display: flex;
            flex-wrap: wrap;

            li {
              display: flex;
              width: 50%;
              font-size: 14px;

              .key {
                display: inline-block;
                width: 120px;
                line-height: 32px;
                text-align: right;

                ::v-deep .text-ov {
                  width: 120px;
                }
              }

              .value-edit {
                display: flex;
                min-width: 480px;
                padding-bottom: 18px;
                overflow: hidden;
                color: #313238;
                text-overflow: ellipsis;
                white-space: nowrap;
                align-items: center;

                .value {
                  max-width: 400px;
                  line-height: 32px;
                }

                .input-list {
                  position: relative;

                  .custom-error {
                    border: 1px solid #ea3636 !important;
                  }

                  .custom-select {
                    ::v-deep .bk-input {
                      border: 1px solid #ea3636 !important;
                    }
                  }

                  .error-text {
                    position: absolute;
                    top: 32px;
                    left: 0;
                    display: inline-block;
                    padding-top: 4px;
                    font-size: 12px;
                    line-height: 1;
                    color: #ea3636;
                  }
                }

                .icon-edit {
                  margin-left: 10px;
                  font-size: 16px;
                  color: #979BA5;
                  cursor: pointer;

                  &:hover {
                    color: #3A84FF;
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

.required-icon {
  display: inline-block;
  margin: 0 3px 0 0;
  line-height: 19px;
  color: #ff5e5e;
  vertical-align: middle;
}

.verify-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 5px;
  vertical-align: middle;
}
</style>
