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
            <img v-if="currentUserInfo.logo" :src="currentUserInfo.logo" />
            <img v-else src="@/images/avatar.png" />
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
            <bk-button>
              取消关联
            </bk-button>
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
                          <bk-radio-button :label="true">基础数据源</bk-radio-button>
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
                  <li>
                    <span class="key">手机号：</span>
                    <div class="value-content">
                      <div class="value-edit" v-if="isEditPhone">
                        <bk-radio-group
                          class="mr8"
                          v-model="currentUserInfo.is_inherited_phone"
                          @change="togglePhone"
                        >
                          <bk-radio-button :label="true">基础数据源</bk-radio-button>
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
                    <span class="value">{{ currentUserInfo.id }}</span>
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
            </li>
          </ul>
        </div>
      </div>
    </template>
  </bk-resize-layout>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { computed, inject, nextTick, onMounted, ref, watch } from 'vue';

import phoneInput from '@/components/phoneInput.vue';
import useValidate from '@/hooks/use-validate';
import {
  getCurrentNaturalUser,
  getPersonalCenterUsers,
  patchUsersEmail,
  patchUsersPhone,
} from '@/http/personalCenterFiles';
import { formatConvert } from '@/utils';

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
const rules = {
  custom_email: [validate.required, validate.email],
};

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

const getCurrentUser = (id) => {
  infoLoading.value = true;
  isEditEmail.value = false;
  isEditPhone.value = false;
  currentNaturalUser.value?.tenant_users.forEach((item) => {
    if (item.id === id) {
      currentTenantInfo.value = item;
    }
  });
  // 关联账户详情
  getPersonalCenterUsers(id).then((res) => {
    currentUserInfo.value = res.data;
    customEmail.value = res.data.custom_email;
    isInheritedEmail.value = currentUserInfo.value.is_inherited_email;
    isInheritedPhone.value = currentUserInfo.value.is_inherited_phone;
    infoLoading.value = false;
  });
};

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
const changeEmail = () => {
  isInheritedEmail.value = currentUserInfo.value.is_inherited_email;
  customEmail.value = currentUserInfo.value.custom_email;
  patchUsersEmail({
    id: currentUserInfo.value.id,
    is_inherited_email: currentUserInfo.value.is_inherited_email,
    custom_email: currentUserInfo.value.custom_email,
  }).then(() => {
    isEditEmail.value = false;
    window.changeInput = false;
  });
};
// 取消编辑邮箱
const cancelEditEmail = () => {
  currentUserInfo.value.is_inherited_email = isInheritedEmail.value;
  currentUserInfo.value.custom_email = customEmail.value;
  isEditEmail.value = false;
  window.changeInput = false;
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
    if (!value) {
      const phoneInput = document.querySelectorAll('.phone-input input');
      phoneInput[0].focus();
    }
  });
};
// 修改手机号
const changePhone = () => {
  isInheritedPhone.value = currentUserInfo.value.is_inherited_phone;
  patchUsersPhone({
    id: currentUserInfo.value.id,
    is_inherited_phone: currentUserInfo.value.is_inherited_phone,
    custom_phone: currentUserInfo.value.custom_phone,
    custom_phone_country_code: currentUserInfo.value.custom_phone_country_code,
  }).then(() => {
    isEditPhone.value = false;
  });
};
// 取消编辑手机号
const cancelEditPhone = () => {
  currentUserInfo.value.is_inherited_phone = isInheritedPhone.value;
  isEditPhone.value = false;
  telError.value = false;
  window.changeInput = false;
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

const changeTelError = (value: boolean) => {
  telError.value = value;
};

const changeCountryCode = (code: string) => {
  currentUserInfo.value.custom_phone_country_code = code;
};
</script>

<style lang="less" scoped>
.personal-center-wrapper {
  height: calc(100vh - 52px);
  min-width: 1600px;

  ::v-deep .bk-resize-layout-aside {
    min-width: 320px;
  }

  ::v-deep .bk-resize-layout-main {
    min-width: calc(1600px - 320px);
  }

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
            font-family: MicrosoftYaHei;
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

        img {
          width: 72px;
          height: 72px;
          object-fit: contain;
          margin-right: 16px;
        }

        .name {
          font-family: MicrosoftYaHei-Bold;
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
                  min-width: 100px;
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
                    font-size: 16px;
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
        }
      }
    }
  }
}
</style>
