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
              （{{ currentNaturalUser.id }}）
            </bk-overflow-title>
            <!-- <i class="user-icon icon-edit" /> -->
          </div>
        </div>
        <div class="left-add">
          <p>
            <span class="account">已关联账号</span>
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
              <div>
                <img v-if="item.logo" :src="item.logo" />
                <img v-else src="@/images/avatar.png" />
                <span class="name text-overflow">{{ item.full_name }}</span>
                <span class="tenant text-overflow">@ {{ item.tenant.name }}</span>
              </div>
              <bk-tag type="filled" theme="success" v-if="currentNaturalUser.full_name === item.full_name">
                当前登录
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
              <p class="name">
                {{ currentTenantInfo.username }}
                <bk-tag>
                  {{ currentTenantInfo.tenant?.id }}
                </bk-tag>
              </p>
              <p class="login-time">最近登录时间：{{ '--' }}</p>
            </div>
          </div>
          <div class="header-right">
            <span v-bk-tooltips="{
              content: '该账号已登录',
              distance: 20,
              disabled: !isCurrentTenant,
            }">
              <bk-button :disabled="isCurrentTenant">
                切换为该账号登录
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
                <p class="item-title">身份信息</p>
              </div>
              <bk-form
                ref="formRef"
                class="item-content"
                :model="currentUserInfo"
                :rules="rules">
                <div class="item-div">
                  <li>
                    <span class="key">用户名：</span>
                    <span class="value">{{ currentUserInfo.username }}</span>
                  </li>
                  <li>
                    <span class="key">全名：</span>
                    <span class="value">{{ currentUserInfo.full_name }}</span>
                  </li>
                  <li>
                    <span class="key">邮箱：</span>
                    <div class="value-content">
                      <div class="value-edit" v-if="isEditEmail">
                        <bk-radio-group
                          class="mr8"
                          v-model="currentUserInfo.is_inherited_email"
                          @change="toggleEmail"
                        >
                          <bk-radio-button :label="true">继承数据源</bk-radio-button>
                          <bk-radio-button :label="false">自定义</bk-radio-button>
                        </bk-radio-group>
                        <bk-input
                          v-if="currentUserInfo.is_inherited_email"
                          v-model="currentUserInfo.email"
                          :disabled="currentUserInfo.is_inherited_email" />
                        <bk-form-item v-else class="email-input" property="custom_email">
                          <bk-input v-model="currentUserInfo.custom_email" />
                        </bk-form-item>
                        <bk-button text theme="primary" class="ml-[12px] mr-[12px]" @click="changeEmail">
                          确定
                        </bk-button>
                        <bk-button text theme="primary" @click="cancelEditEmail">
                          取消
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
                        <i class="user-icon icon-edit" @click="isEditEmail = true" />
                      </div>
                    </div>
                  </li>
                  <li class="mb-[10px]">
                    <span class="key">手机号：</span>
                    <div class="value-content">
                      <div class="value-edit" v-if="isEditPhone">
                        <bk-radio-group
                          class="mr8"
                          v-model="currentUserInfo.is_inherited_phone"
                          @change="togglePhone"
                        >
                          <bk-radio-button :label="true">继承数据源</bk-radio-button>
                          <bk-radio-button :label="false">自定义</bk-radio-button>
                        </bk-radio-group>
                        <bk-form-item
                          v-if="currentUserInfo.is_inherited_phone"
                          class="phone-input">
                          <phoneInput
                            :form-data="currentUserInfo"
                            :disabled="currentUserInfo.is_inherited_phone" />
                        </bk-form-item>
                        <bk-form-item v-else class="phone-input">
                          <phoneInput
                            :form-data="currentUserInfo"
                            :tel-error="telError"
                            :custom="true"
                            @changeCountryCode="changeCountryCode"
                            @changeTelError="changeTelError" />
                        </bk-form-item>
                        <bk-button text theme="primary" class="ml-[12px] mr-[12px]" @click="changePhone">
                          确定
                        </bk-button>
                        <bk-button text theme="primary" @click="cancelEditPhone">
                          取消
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
                        <i class="user-icon icon-edit" @click="isEditPhone = true" />
                      </div>
                    </div>
                  </li>
                </div>
                <div class="item-div">
                  <li>
                    <span class="key">所属租户ID：</span>
                    <span class="value">{{ currentTenantInfo.tenant?.id }}</span>
                  </li>
                  <li>
                    <span class="key">所属组织：</span>
                    <span class="value">{{ formatConvert(currentUserInfo.departments) }}</span>
                  </li>
                  <li>
                    <span class="key">直属上级：</span>
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
                  <bk-overflow-title class="key" type="tips">{{ item.display_name }}：</bk-overflow-title>
                  <div class="value-edit custom-input">
                    <span v-if="!item.isEdit" class="value">
                      {{ ConvertVal(item) }}
                    </span>
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
                        必填项
                      </span>
                    </div>
                    <i
                      v-if="item.editable && !item.isEdit"
                      class="user-icon icon-edit"
                      @click="editExtra(item, index)" />
                    <div v-if="item.isEdit" style="line-height: 32px;">
                      <bk-button text theme="primary" class="ml-[12px] mr-[12px]" @click="changeCustomFields(item)">
                        确定
                      </bk-button>
                      <bk-button text theme="primary" @click="cancelCustomFields(item, index)">
                        取消
                      </bk-button>
                    </div>
                  </div>
                </li>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </template>
  </bk-resize-layout>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, Message } from 'bkui-vue';
import { computed, inject, nextTick, onMounted, ref, watch } from 'vue';

import phoneInput from '@/components/phoneInput.vue';
import useValidate from '@/hooks/use-validate';
import { useCustomFields } from '@/hooks/useCustomFields';
import {
  getCurrentNaturalUser,
  getPersonalCenterUsers,
  getPersonalCenterUserVisibleFields,
  patchTenantUsersLogo,
  patchUsersEmail,
  patchUsersPhone,
  putPersonalCenterUserExtrasFields,
} from '@/http/personalCenterFiles';
import { formatConvert, getBase64 } from '@/utils';

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
const rules = {
  custom_email: [validate.required, validate.email],
};
const formRef = ref();
// 保存修改后的extras数据
const extrasList = ref([]);

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
    isEditEmail.value = false;
    isEditPhone.value = false;
    currentNaturalUser.value?.tenant_users.forEach((item) => {
      if (item.id === id) {
        currentTenantInfo.value = item;
      }
    });
    // 关联账户详情
    const res = await getPersonalCenterUsers(id);
    currentUserInfo.value = res.data;
    const fieldsRes = await getPersonalCenterUserVisibleFields(id);
    currentUserInfo.value.extras = useCustomFields(currentUserInfo.value?.extras, fieldsRes.data.custom_fields);
    extrasList.value = JSON.parse(JSON.stringify(currentUserInfo.value.extras));
    customEmail.value = res.data.custom_email;
    customPhone.value = res.data.custom_phone;
    customPhoneCode.value = res.data.custom_phone_country_code;
    isInheritedEmail.value = currentUserInfo.value.is_inherited_email;
    isInheritedPhone.value = currentUserInfo.value.is_inherited_phone;
  } catch (error) {
    console.warn(error);
  } finally {
    infoLoading.value = false;
  }
};

const ConvertVal = (item: any) => {
  return item.value === '' ? '--' : (item.data_type === 'multi_enum' ? item.value?.join(' ; ') : item.value);
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
  } catch (error) {
    console.warn(error);
  }
};
// 取消自定义字段修改
const cancelCustomFields = (item, index) => {
  item.value = extrasList.value[index]?.value;
  item.isEdit = false;
  item.error = false;
};

watch(() => currentUserInfo.value?.extras, (val) => {
  if (val.length) {
    const allFalse = val.every((item) => !item.isEdit);
    window.changeInput = !(allFalse && isEditEmail.value === false && isEditPhone.value === false);
  }
}, {
  deep: true,
});

const tagTheme = value => (value ? 'info' : 'warning');
const tagText = value => (value ? '数据源' : '自定义');

const isEditEmail = ref(false);

watch(() => isEditEmail.value, (val) => {
  if (val) {
    window.changeInput = true;
  }
});

const isCurrentTenant = computed(() => currentNaturalUser.value.full_name === currentTenantInfo.value.full_name);

// 切换邮箱
const toggleEmail = (value) => {
  nextTick(() => {
    if (!value) {
      currentUserInfo.value.custom_email = customEmail.value;
      const emailInput = document.querySelectorAll('.email-input input');
      emailInput[0].focus();
    }
  });
};
// 修改邮箱
const changeEmail = async () => {
  await formRef.value.validate();
  isInheritedEmail.value = currentUserInfo.value.is_inherited_email;
  customEmail.value = currentUserInfo.value.custom_email;
  patchUsersEmail({
    id: currentUserInfo.value.id,
    is_inherited_email: currentUserInfo.value.is_inherited_email,
    custom_email: currentUserInfo.value.custom_email,
  }).then(() => {
    isEditEmail.value = false;
    isEditFn();
  });
};
// 取消编辑邮箱
const cancelEditEmail = () => {
  currentUserInfo.value.is_inherited_email = isInheritedEmail.value;
  currentUserInfo.value.custom_email = customEmail.value;
  isEditEmail.value = false;
  isEditFn();
};

const isEditPhone = ref(false);

watch(() => isEditPhone.value, (val) => {
  if (val) {
    window.changeInput = true;
  }
});

// 切换手机号
const togglePhone = (value) => {
  nextTick(() => {
    if (value) return telError.value = false;
    currentUserInfo.value.custom_phone = customPhone.value;
    const phoneInput = document.querySelectorAll('.phone-input input');
    phoneInput[0].focus();
  });
};
// 修改手机号
const changePhone = () => {
  if (telError.value) return;
  isInheritedPhone.value = currentUserInfo.value.is_inherited_phone;
  customEmail.value = currentUserInfo.value.custom_phone;
  patchUsersPhone({
    id: currentUserInfo.value.id,
    is_inherited_phone: currentUserInfo.value.is_inherited_phone,
    custom_phone: currentUserInfo.value.custom_phone,
    custom_phone_country_code: currentUserInfo.value.custom_phone_country_code,
  }).then(() => {
    isEditPhone.value = false;
    isEditFn();
  });
};
// 取消编辑手机号
const cancelEditPhone = () => {
  currentUserInfo.value.is_inherited_phone = isInheritedPhone.value;
  currentUserInfo.value.custom_phone = customPhone.value;
  currentUserInfo.value.custom_phone_country_code = customPhoneCode.value;
  isEditPhone.value = false;
  telError.value = false;
  isEditFn();
};
// 切换关联账号
const handleClickItem = async (item) => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
  getCurrentUser(item.id);
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
    Message({ theme: 'error', message: '图片大小超出限制，请重新上传' });
  }
};

// 是否是编辑状态
const isEditFn = () => {
  const allFalse = currentUserInfo.value?.extras.every((item) => !item.isEdit);
  window.changeInput = !(allFalse && isEditEmail.value === false && isEditPhone.value === false);
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

          .name {
            display: inline-block;
            max-width: 100px;
            margin: 0 8px;
            font-size: 14px;
            color: #313238;
          }

          .tenant {
            display: inline-block;
            max-width: 100px;
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

        .name {
          font-size: 32px;
          font-weight: 700;

          .bk-tag {
            font-weight: 400;
          }
        }

        .login-time {
          font-size: 14px;
        }
      }
    }

    .personal-center-details {
      height: calc(100vh - 196px);
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
</style>
