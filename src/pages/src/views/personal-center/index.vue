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
            <span class="name">{{ currentNaturalUser.full_name }}</span>
            <span class="id">（{{ currentNaturalUser.id }}）</span>
            <i class="user-icon icon-edit" />
          </div>
        </div>
        <div class="left-add">
          <p>
            <span class="account">已关联账号</span>
            <span class="number">{{ currentNaturalUser.tenant_users?.length }}</span>
          </p>
          <bk-button theme="primary" text>
            <i class="user-icon icon-add-2 mr8" />
            新增关联
          </bk-button>
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
                <span class="name">{{ item.username }}</span>
                <span class="tenant">@ {{ item.tenant.name }}</span>
              </div>
              <bk-tag type="filled" theme="success" v-if="currentNaturalUser.id === item.id">
                当前登录
              </bk-tag>
            </div>
          </li>
        </ul>
      </div>
    </template>
    <template #main>
      <div class="personal-center-main">
        <header>
          <div class="header-left">
            <img v-if="currentUserInfo.logo" :src="currentUserInfo.logo" />
            <img v-else src="@/images/avatar.png" />
            <div>
              <p class="name">
                {{ currentUserInfo.username }}
                <bk-tag>
                  {{ currentUserInfo.id }}
                </bk-tag>
              </p>
              <p class="login-time">最近登录时间：{{ '--' }}</p>
            </div>
          </div>
          <div class="header-right">
            <span v-bk-tooltips="{ content: '该账号已登录', distance: 20 }">
              <bk-button>
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
              <ul class="item-content">
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
                        >
                          <bk-radio-button :label="true">基础数据源</bk-radio-button>
                          <bk-radio-button :label="false">自定义</bk-radio-button>
                        </bk-radio-group>
                        <bk-input
                          v-if="currentUserInfo.is_inherited_email"
                          v-model="currentUserInfo.email"
                          :disabled="currentUserInfo.is_inherited_email" />
                        <bk-input
                          v-else
                          v-model="currentUserInfo.custom_email" />
                        <bk-button text theme="primary" class="ml-[12px] mr-[12px]" @click="changeEmail">
                          确定
                        </bk-button>
                        <bk-button text theme="primary" @click="isEditEmail = false">
                          取消
                        </bk-button>
                      </div>
                      <div v-else>
                        <bk-tag :theme="tagTheme(currentUserInfo.is_inherited_email)">
                          {{ tagText(currentUserInfo.is_inherited_email) }}
                        </bk-tag>
                        <span class="value">{{ currentUserInfo.email }}</span>
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
                        >
                          <bk-radio-button :label="true">基础数据源</bk-radio-button>
                          <bk-radio-button :label="false">自定义</bk-radio-button>
                        </bk-radio-group>
                        <bk-input
                          v-if="currentUserInfo.is_inherited_phone"
                          v-model="currentUserInfo.phone"
                          :disabled="currentUserInfo.is_inherited_phone" />
                        <bk-input
                          v-else
                          v-model="currentUserInfo.custom_phone" />
                        <bk-button text theme="primary" class="ml-[12px] mr-[12px]" @click="changePhone">
                          确定
                        </bk-button>
                        <bk-button text theme="primary" @click="isEditPhone = false">
                          取消
                        </bk-button>
                      </div>
                      <div v-else>
                        <bk-tag :theme="tagTheme(currentUserInfo.is_inherited_phone)">
                          {{ tagText(currentUserInfo.is_inherited_phone) }}
                        </bk-tag>
                        <span class="value">{{ currentUserInfo.phone }}</span>
                        <i class="user-icon icon-edit" @click="isEditPhone = true" />
                      </div>
                    </div>
                  </li>
                </div>
                <div class="item-div">
                  <li>
                    <span class="key">所属租户ID：</span>
                    <span class="value">{{ currentUserInfo.tenant?.id }}</span>
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
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </template>
  </bk-resize-layout>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { onMounted, ref } from 'vue';

import { formatConvert } from '@/utils';

const currentNaturalUser = ref({});
// 当前用户信息
const currentUserInfo = ref({});

const isLoading = ref(false);

onMounted(() => {
  getNaturalUser();
  getCurrentUser();
});

const getNaturalUser = () => {
  currentNaturalUser.value = {
    id: '55678446',
    full_name: 'Eric',
    tenant_users: [
      {
        id: '55678446',
        tenant: {
          id: '1',
          name: '默认租户',
        },
        username: 'Eric Lee',
        full_name: 'Eric Lee',
        logo: '',
      },
      {
        id: '12345',
        tenant: {
          id: '1',
          name: 'local-test',
        },
        username: 'Eric Li',
        full_name: 'Eric Li',
        logo: '',
      },
    ],
  };
};

const getCurrentUser = () => {
  currentUserInfo.value = {
    id: 'local-test',
    username: 'Eric Lee',
    full_name: 'Eric Lee（李英杰）',
    logo: '',
    tenant: {
      id: 'local-test-test',
      name: '租户名称',
    },
    email: '124567345@qq.com',
    phone: '15756734555',
    phone_country_code: '86',
    departments: [
      { id: '3', name: '总公司' },
      { id: '3', name: '分公司' },
    ],
    leaders: [
      { id: '4', name: '张三' },
      { id: '4', name: '李四' },
    ],
    custom_email: '',
    custom_phone: '',
    custom_phone_country_code: '',
    is_inherited_email: true,
    is_inherited_phone: true,
  };
};

const tagTheme = value => (value ? 'info' : 'warning');
const tagText = value => (value ? '数据源' : '自定义');

const isEditEmail = ref(false);
const changeEmail = () => {
  isEditEmail.value = false;
};

const isEditPhone = ref(false);
const changePhone = () => {
  isEditPhone.value = false;
};

const handleClickItem = (item) => {
  currentUserInfo.value.id = item.id;
  currentUserInfo.value.username = item.username;
  currentUserInfo.value.full_name = item.full_name;
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
          margin-left: 8px;
          font-size: 14px;
          font-weight: 700;
        }

        .id {
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

          img {
            display: inline-block;
            width: 22px;
            height: 22px;
            vertical-align: middle;
            object-fit: contain;
          }

          .name {
            display: inline-block;
            margin: 0 8px;
            font-family: MicrosoftYaHei;
            font-size: 14px;
            color: #313238;
          }

          .tenant {
            color: #ff9c01;
          }
        }
      }

      .isActive {
        background-color: #e1ecff;
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
                line-height: 40px;

                .key {
                  display: inline-block;
                  min-width: 100px;
                  text-align: right;
                }

                .value {
                  color: #313238;
                }

                .value-content {
                  .value-edit {
                    display: flex;
                    align-items: center;
                    height: 40px;

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
