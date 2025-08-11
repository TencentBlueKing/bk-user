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
      <AsideList
        :current-user-id="currentUserInfo.id"
        :current-natural-user="currentNaturalUser"
        @change="(id) => getCurrentUser(id)"
      />
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
              <!-- <p class="login-time">{{ $t('最近登录时间') }}：{{ '--' }}</p> -->
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
              <!-- <bk-button :disabled="isCurrentTenant">
                {{ $t('切换为该账号登录') }}
              </bk-button> -->
            </span>
            <!-- <bk-button>
              取消关联
            </bk-button> -->
          </div>
        </header>
        <InfoCard :title="$t('身份信息')">
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
                  <div class="value-edit" v-if="isEditEmail">
                    <bk-select
                      class="bk-select"
                      v-model="emailSelect"
                      @change="toggleEmail"
                      :filterable="false"
                      :clearable="false">
                      <bk-option :id="OpenDialogSelect.inherit" :key="0" :name="$t('继承数据源')"></bk-option>
                      <bk-option :id="OpenDialogSelect.custom" :key="1" :name="$t('自定义')"></bk-option>
                    </bk-select>
                    <bk-input
                      v-if="emailSelect === OpenDialogSelect.inherit"
                      v-model="currentUserInfo.email"
                      :disabled="true" />
                    <bk-form-item v-else class="email-input" property="custom_email">
                      <bk-input v-model="currentUserInfo.custom_email" @enter="changeEmail" autofocus />
                    </bk-form-item>
                    <bk-button
                      text theme="primary" class="ml-[12px] mr-[12px]"
                      @click="changeEmail"
                      v-if="emailUpdateRestriction === emailEditable.YES
                        || emailSelect === OpenDialogSelect.inherit">
                      {{ $t('确定') }}
                    </bk-button>
                    <bk-button
                      text theme="primary" class="ml-[12px] mr-[12px]"
                      @click="verifyIdentityInfo(
                        OpenDialogType.email,
                        {
                          email: currentUserInfo.custom_email
                        }
                      )"
                      v-if="emailUpdateRestriction === emailEditable.Verify
                        && emailSelect === OpenDialogSelect.custom">
                      {{ $t('验证') }}
                    </bk-button>
                    <bk-button text theme="primary" @click="cancelEditEmail" class="leading-[19px]">
                      {{ $t('取消') }}
                    </bk-button>
                  </div>
                  <div v-else>
                    <bk-tag :theme="tagTheme(currentUserInfo.is_inherited_email)">
                      {{ tagText(currentUserInfo.is_inherited_email) }}
                    </bk-tag>
                    <span class="value">
                      {{ currentUserInfo.is_inherited_email
                        ? currentUserInfo.email
                        : currentUserInfo.custom_email }}
                    </span>
                    <i
                      v-if="emailUpdateRestriction !== emailEditable.No"
                      class="user-icon icon-edit"
                      @click="isEditEmail = true">
                    </i>
                  </div>
                </div>
              </li>
              <li class="mb-[10px]">
                <span class="key">
                  <span class="required-icon"> * </span>
                  {{ $t('手机号') }}：</span>
                <div class="value-content">
                  <div class="value-edit" v-if="isEditPhone">
                    <bk-select
                      class="bk-select"
                      v-model="phoneSelect"
                      @change="togglePhone"
                      :filterable="false"
                      :clearable="false">
                      <bk-option :id="OpenDialogSelect.inherit" :key="0" :name="$t('继承数据源')"></bk-option>
                      <bk-option :id="OpenDialogSelect.custom" :key="0" :name="$t('自定义')"></bk-option>
                    </bk-select>
                    <bk-form-item
                      v-if="phoneSelect === OpenDialogSelect.inherit"
                      class="phone-input">
                      <phoneInput
                        class="phone-input-input"
                        :form-data="currentUserInfo"
                        :disabled="true"
                        autofocus="autofocus"
                      />
                    </bk-form-item>
                    <bk-form-item v-else class="phone-input">
                      <phoneInput
                        class="phone-input-input"
                        :form-data="currentUserInfo"
                        :tel-error="telError"
                        :custom="true"
                        custom-tel-error-text="请输入正确的手机号格式"
                        @change-country-code="changeCountryCode"
                        @change-tel-error="changeTelError"
                        @keydown.enter="changePhone" />
                    </bk-form-item>
                    <bk-button
                      text theme="primary" class="ml-[12px] mr-[12px]"
                      @click="changePhone"
                      v-if="phoneUpdateRestriction === phoneEditable.YES
                        || phoneSelect === OpenDialogSelect.inherit">
                      {{ $t('确定') }}
                    </bk-button>
                    <bk-button
                      text theme="primary" class="ml-[12px] mr-[12px]"
                      @click="verifyIdentityInfo(
                        OpenDialogType.phone,
                        {
                          phone: currentUserInfo.custom_phone,
                          phone_country_code: currentUserInfo.custom_phone_country_code
                        }
                      )"
                      v-if="phoneUpdateRestriction === phoneEditable.Verify
                        && phoneSelect === OpenDialogSelect.custom">
                      {{ $t('验证') }}
                    </bk-button>
                    <bk-button text theme="primary" @click="cancelEditPhone" class="leading-[19px]">
                      {{ $t('取消') }}
                    </bk-button>
                  </div>
                  <div v-else>
                    <bk-tag :theme="tagTheme(currentUserInfo.is_inherited_phone)">
                      {{ tagText(currentUserInfo.is_inherited_phone) }}
                    </bk-tag>
                    <span class="value">
                      {{ currentUserInfo.is_inherited_phone
                        ? currentUserInfo.phone
                        : currentUserInfo.custom_phone }}
                    </span>
                    <i
                      v-if="phoneUpdateRestriction !== phoneEditable.No"
                      class="user-icon icon-edit"
                      @click="isEditPhone = true">
                    </i>
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
                    @change="changeSelect(item)"
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
        </InfoCard>
        <InfoCard :title="$t('语言和时区')">
          <bk-form
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
                    <bk-button text theme="primary" class="ml-[12px] mr-[12px]" @click="submitChange(item)">
                      {{ $t('确定') }}
                    </bk-button>
                    <bk-button text theme="primary" @click="cancelChange(item)">{{ $t('取消') }}</bk-button>
                  </div>
                  <div v-else>
                    <span class="value">
                      {{ item.model === 'language' ?
                        showLanguage(currentUserInfo[item.model])
                        : currentUserInfo[item.model]}}
                    </span>
                    <i class="user-icon icon-edit" @click="item.isEdit = true" />
                  </div>
                </div>
              </li>
            </div>
          </bk-form>
        </InfoCard>
      </div>
      <!-- 修改密码 -->
      <ChangePassword
        :config="passwordModalConfig"
        @closed="hidePasswordModal" />
      <!-- 邮箱、手机号编辑验证 -->
      <EmailVerify
        v-model:is-show="showEmailVerify"
        :initial-data="emailInitialData"
        :user-id="currentUserInfo.id"
        :cur-email-text="curEmail"
        @confirm-verify-email="verifyEmail"
      />
      <PhoneVerify
        v-model:is-show="showPhoneVerify"
        :initial-data="phoneInitialData"
        :user-id="currentUserInfo.id"
        :cur-email-text="curPhone"
        @confirm-verify-phone="verifyPhone"
      />
    </template>
  </bk-resize-layout>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, Message } from 'bkui-vue';
import { UploadRequestOptions } from 'bkui-vue/lib/upload/upload.type';
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue';

import AsideList from './AsideList.vue';
import EmailVerify from './EmailVerify.vue';
import { emailEditable, OpenDialogSelect, OpenDialogType, phoneEditable  } from './openDialogType';
import PhoneVerify from './PhoneVerify.vue';

import ChangePassword from '@/components/ChangePassword.vue';
import InfoCard from '@/components/InfoCard.vue';
import phoneInput from '@/components/phoneInput.vue';
import { ExtrasCustomFields, useCustomFields, useValidate } from '@/hooks';
import {
  getCurrentNaturalUser,
  getPersonalCenterUserFeature,
  getPersonalCenterUsers,
  getPersonalCenterUserVisibleFields,
  patchTenantUsersLogo,
  patchUsersEmail,
  patchUsersPhone,
  putPersonalCenterUserExtrasFields,
  putUserLanguage,
  putUserTimeZone,
} from '@/http';
import { CurrentNaturalUserData, PersonalCenterUsersData } from '@/http/types/personalCenterFiles';
import { t } from '@/language/index';
import { useUser } from '@/store/user';
import { customFieldsMap, formatConvert, getBase64, handleSwitchLocale, LANGUAGE_OPTIONS, TIME_ZONES } from '@/utils';

const userStore = useUser();
const validate = useValidate();
const currentNaturalUser = ref<CurrentNaturalUserData>({} as CurrentNaturalUserData);

type OperateExtrasCustomFields = (ExtrasCustomFields & {
  isEdit?: boolean
  error?: boolean
});

type CurrentUserInfo = PersonalCenterUsersData & {
  extras: OperateExtrasCustomFields[]
};
// 当前用户信息
const currentUserInfo = ref<CurrentUserInfo>({} as CurrentUserInfo);
// 当前租户信息
const currentTenantInfo = ref({} as CurrentNaturalUserData['tenant_users'][number]);

const isLoading = ref(false);
const infoLoading = ref(false);
const isInheritedEmail = ref(true);
const isInheritedPhone = ref(true);
// 缓存用户自定义邮箱、手机号，仅当自定义数据为验证后的数据时才缓存
const customEmail = ref('');
const customPhone = ref('');
const customPhoneCode = ref('');
const originalValue = ref<{
  language: string
  time_zone: string
}>({
  language: '',
  time_zone: '',
});
const rules = {
  custom_email: [validate.required, validate.email],
};
const formRef = ref();
// 保存修改后的extras数据
const extrasList = ref<OperateExtrasCustomFields[]>([]);
// 是否可以修改密码
const canChangePassword = ref(false);
// 是否可以修改邮箱
const emailUpdateRestriction = ref<emailEditable>(emailEditable.Verify);
// 是否可以修改手机
const phoneUpdateRestriction = ref<phoneEditable>(phoneEditable.Verify);


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

const getCurrentUser = async (id: string) => {
  try {
    infoLoading.value = true;
    isEditEmail.value = false;
    isEditPhone.value = false;
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
    emailUpdateRestriction.value = featureRes.data.email_update_restriction as emailEditable;
    phoneUpdateRestriction.value = featureRes.data.phone_update_restriction as phoneEditable;
    extrasList.value = [...currentUserInfo.value.extras];
    // 初始化时读取custom data
    customEmail.value = userRes.data.custom_email;
    customPhone.value = userRes.data.custom_phone;
    customPhoneCode.value = userRes.data.custom_phone_country_code;
    isInheritedEmail.value = currentUserInfo.value.is_inherited_email;
    isInheritedPhone.value = currentUserInfo.value.is_inherited_phone;
    originalValue.value = {
      language: currentUserInfo.value.language,
      time_zone: currentUserInfo.value.time_zone,
    };

    // 根据当前用户是否继承了邮箱和手机，决定是否重置custom缓存
    if (currentUserInfo.value.is_inherited_email) {
      currentUserInfo.value.custom_email = '';
      customEmail.value = '';
    }
    if (currentUserInfo.value.is_inherited_phone) {
      currentUserInfo.value.custom_phone = '';
      customPhone.value = '';
    }
  } catch (error) {
    console.warn(error);
  } finally {
    infoLoading.value = false;
  }
};

// 获取当前编辑框焦点
const editExtra = (item: OperateExtrasCustomFields, index: number) => {
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
const customBlur = (item: OperateExtrasCustomFields) => {
  item.error = item.value === '' || (item.data_type === 'multi_enum' && !item.value.length);
};

const handleInput = (item: OperateExtrasCustomFields) => {
  item.error = false;
};
// 改变枚举值
const changeSelect = (item: OperateExtrasCustomFields) => {
  item.value = item.value;
  item.error = false;
};

const clearSelect = (item: OperateExtrasCustomFields) => {
  item.error = true;
};
// 提交修改自定义字段
const changeCustomFields = async (item: OperateExtrasCustomFields) => {
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

const showLanguage = computed(() => (targetValue: string) => {
  const foundItem = LANGUAGE_OPTIONS?.find(item => item.value === targetValue);
  return foundItem ? foundItem.label : null;
});

const submitChange  = async (item: LanguageAndTimeZoneFieldItem) => {
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
      setTimeout(() => handleSwitchLocale(currentUserInfo.value.language, userStore.user.tenant_id), 100);
    }
    originalValue.value[model] = currentUserInfo.value[model];
  } catch (error) {
    console.warn(error);
  }
};

const cancelChange = (item: LanguageAndTimeZoneFieldItem) => {
  item.isEdit = false;
  currentUserInfo.value[item.model] = originalValue.value[item.model];
};

type LanguageAndZoneModelField = 'language' | 'time_zone';
type LanguageAndTimeZoneFieldItem = {
  label: string
  isEdit: boolean
  model: LanguageAndZoneModelField
  options: {
    value: string
    label: string
  }[]
};

type LanguageTimeZoneField = Record<string, LanguageAndTimeZoneFieldItem>;

const LanguageAndTimeZone = ref<LanguageTimeZoneField>({
  language: {
    label: t('语言'),
    isEdit: false,
    model: 'language',
    options: LANGUAGE_OPTIONS,
  },
  timeZone: {
    label: t('时区'),
    isEdit: false,
    model: 'time_zone',
    options: TIME_ZONES,
  },
});

// 取消自定义字段修改
const cancelCustomFields = (item: OperateExtrasCustomFields, index: number) => {
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

const tagTheme = (value: boolean) => (value ? 'info' : 'warning');
const tagText = (value: boolean) => (value ? t('继承数据源') : t('自定义'));

const isEditEmail = ref(false);

watch(() => isEditEmail.value, (val) => {
  if (val) {
    window.changeInput = true;
  }
});

const isCurrentTenant = computed(() => currentNaturalUser.value.full_name === currentTenantInfo.value.full_name);

// 切换邮箱
const toggleEmail = (value: OpenDialogSelect) => {
  const currentInherit = value === OpenDialogSelect.inherit;
  currentUserInfo.value.is_inherited_email = currentInherit;
  nextTick(() => {
    if (!currentInherit) {
      currentUserInfo.value.custom_email = customEmail.value;
      const emailInput = document.querySelectorAll('.email-input input');
      (emailInput[0] as HTMLInputElement)?.focus();
    }
  });
};
// 修改邮箱
const changeEmail = async () => {
  const result = await formRef.value.validate().catch(() => false);
  if (!result) return;
  patchUsersEmail({
    id: currentUserInfo.value.id,
    is_inherited_email: currentUserInfo.value.is_inherited_email,
    custom_email: currentUserInfo.value.custom_email === '--' ? '' : currentUserInfo.value.custom_email,
  }).then(() => {
    isEditEmail.value = false;
    isEditing();
    isInheritedEmail.value = currentUserInfo.value.is_inherited_email;
    if (!currentUserInfo.value.is_inherited_email) {
      customEmail.value = currentUserInfo.value.custom_email;
    }
    Message({ theme: 'success', message: t('保存成功') });
  });
};

const verifyEmail = (data: any) => {
  isEditEmail.value = false;
  isEditing();
  isInheritedEmail.value = false;
  customEmail.value = data.custom_email;
  currentUserInfo.value.custom_email = data.custom_email;
};

// 取消编辑邮箱
const cancelEditEmail = () => {
  currentUserInfo.value.is_inherited_email = isInheritedEmail.value;
  currentUserInfo.value.custom_email = customEmail.value;
  isEditEmail.value = false;
  isEditing();
};

const isEditPhone = ref(false);

watch(() => isEditPhone.value, (val) => {
  if (val) {
    window.changeInput = true;
  }
});

const emailSelect = computed(() => (currentUserInfo.value.is_inherited_email === false
  ? OpenDialogSelect.custom
  : OpenDialogSelect.inherit));

const phoneSelect = computed(() => (currentUserInfo.value.is_inherited_phone === false
  ? OpenDialogSelect.custom
  : OpenDialogSelect.inherit));

// 切换手机号
const togglePhone = (value: OpenDialogSelect) => {
  const currentInherit = value === OpenDialogSelect.inherit;
  currentUserInfo.value.is_inherited_phone = currentInherit;
  nextTick(() => {
    if (currentInherit) return telError.value = false;
    // toggle Select本身不处理缓存清空，仅读取缓存
    // 与input双向绑定的数据为 currentUSerInfo.value.custom_phone
    currentUserInfo.value.custom_phone = customPhone.value;
    const phoneInput = document.querySelectorAll('.phone-input input');
    (phoneInput[0] as HTMLInputElement).focus();
  });
};
// 修改手机号
const changePhone = () => {
  if (telError.value) return;
  patchUsersPhone({
    id: currentUserInfo.value.id,
    is_inherited_phone: currentUserInfo.value.is_inherited_phone,
    custom_phone: currentUserInfo.value.custom_phone === '--' ? '' : currentUserInfo.value.custom_phone,
    custom_phone_country_code: currentUserInfo.value.custom_phone_country_code,
  }).then(() => {
    isEditPhone.value = false;
    isEditing();
    isInheritedPhone.value = currentUserInfo.value.is_inherited_phone;
    // 若当前为自定义，更新缓存
    if (!currentUserInfo.value.is_inherited_phone) {
      customPhone.value = currentUserInfo.value.custom_phone;
    }
    Message({ theme: 'success', message: t('保存成功') });
  });
};

const verifyPhone = (data: any) => {
  isEditPhone.value = false;
  isEditing();
  isInheritedPhone.value = false;
  customPhone.value = data.custom_phone;
  currentUserInfo.value.custom_phone = data.custom_phone;
  customPhoneCode.value = data.custom_phone_country_code;
  currentUserInfo.value.custom_phone_country_code = data.custom_phone_country_code;
};

// 取消编辑手机号
const cancelEditPhone = () => {
  currentUserInfo.value.is_inherited_phone = isInheritedPhone.value;
  currentUserInfo.value.custom_phone = customPhone.value;
  currentUserInfo.value.custom_phone_country_code = customPhoneCode.value;
  isEditPhone.value = false;
  telError.value = false;
  isEditing();
};

const telError = ref(false);

const changeTelError = (value: boolean, phone: string) => {
  telError.value = value;
  currentUserInfo.value.custom_phone = phone;
};

const changeCountryCode = (code: string) => {
  currentUserInfo.value.custom_phone_country_code = code;
};

const handleRes = (response: any) => {
  if (response.id) {
    return true;
  }
  return false;
};

const showEmailVerify = ref(false);
const showPhoneVerify = ref(false);

watch(showPhoneVerify, (newShow) => {
  if (!newShow) telError.value = false;
});

interface EmailInitialData {
  email: string,
}
interface PhoneInitialData {
  phone: string,
  phone_country_code: string
}
const emailInitialData = reactive<EmailInitialData>({
  email: '',
});
const phoneInitialData = reactive<PhoneInitialData>({
  phone: '',
  phone_country_code: '',
});

// 验证身份信息下的邮箱或手机号
const verifyIdentityInfo = async (type: OpenDialogType, value: any) => {
  if (type === OpenDialogType.phone && !telError.value) {
    phoneInitialData.phone = value.phone;
    phoneInitialData.phone_country_code = value.phone_country_code;
    showPhoneVerify.value = true;
  }
  if (type === OpenDialogType.email) {
    const result = await formRef.value.validate();
    if (!result) return;
    emailInitialData.email = value.email;
    showEmailVerify.value = true;
  }
};
const curEmail = computed<string>(() => {
  const result: string = currentUserInfo.value.is_inherited_email
    ? currentUserInfo.value.email
    : currentUserInfo.value.custom_email;
  return result === '--' ? '' : result;
});
const curPhone = computed<string>(() => {
  const result: string = currentUserInfo.value.is_inherited_phone
    ? currentUserInfo.value.phone
    : currentUserInfo.value.custom_phone;
  return result === '--' ? '' : result;
});

const customRequest = (event: UploadRequestOptions) => {
  getBase64(event.file).then((res) => {
    currentUserInfo.value.logo = res as string;
    patchTenantUsersLogo({
      id: currentUserInfo.value.id,
      logo: currentUserInfo.value.logo,
    });
  })
    .catch((e) => {
      console.warn(e);
    });
};

const handleError = (file: File) => {
  if (file.size > (2 * 1024 * 1024)) {
    Message({ theme: 'error', message: t('图片大小超出限制，请重新上传') });
  }
};

// 是否是编辑状态
const isEditing = () => {
  const allFalse = currentUserInfo.value?.extras.every(item => !item.isEdit);
  window.changeInput = !(allFalse && isEditEmail.value === false && isEditPhone.value === false);
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
              .bk-select {
                width: 106px;
                line-height: 0px;
              }
              .email-input {
                height: 32px;
                .bk-form-content {
                  height: 100%;
                  .bk-input--text {
                    height: 100%;
                  }
                }
              }
              .phone-input {
                width: 269px;
                margin-left: -1px;
                ::v-deep .iti__tel-input {
                  border-top-left-radius: 0px;
                  border-bottom-left-radius: 0px;
                }
              }

              .bk-input {
                width: 269px;
                margin: -1px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
              }

              ::v-deep .bk-button-text {
                line-height: 19px;
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

.required-icon {
  display: inline-block;
  margin: 0 3px 0 0;
  line-height: 19px;
  color: #ff5e5e;
  vertical-align: middle;
}
</style>
