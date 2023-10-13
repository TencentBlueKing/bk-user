<template>
  <div class="login-setting-content user-scroll-y">
    <!-- <div class="setting-item">
      <p class="item-title">登录方式设置</p>
      <bk-form class="setting-form" form-type="vertical">
        <bk-form-item label="基本登录" description="至少选择一种默认方式">
          <bk-checkbox-group>
            <bk-checkbox
              class="hover-checkbox"
              v-for="item in state.basicLogin"
              :key="item.value"
              :label="item.name"
            >
              {{ item.name }}
              <bk-tag theme="info" v-if="item.default">默认</bk-tag>
            </bk-checkbox>
          </bk-checkbox-group>
        </bk-form-item>
        <bk-form-item label="个人社交账号登录">
          <bk-checkbox-group>
            <bk-checkbox
              v-for="item in state.accountLogin"
              :key="item.value"
              :label="item.name"
            >
              {{ item.name }}
            </bk-checkbox>
          </bk-checkbox-group>
        </bk-form-item>
      </bk-form>
    </div> -->
    <div class="setting-item">
      <p class="item-title">MFA认证方式</p>
      <bk-form class="setting-form" form-type="vertical">
        <bk-form-item label="MFA认证方式">
          <bk-checkbox-group>
            <bk-checkbox label="手机号+验证码" />
            <bk-checkbox label="邮箱+验证码" />
          </bk-checkbox-group>
        </bk-form-item>
        <div class="item-flex">
          <bk-form-item label="强制开启MFA" description="强制开启MFA">
            <bk-switcher v-model="state.openMFA" theme="primary" size="large" />
          </bk-form-item>
          <bk-form-item label="启用范围">
            <div class="add-wrapper">
              <bk-button theme="primary" text v-if="!isShow" @click="handleClickAdd">
                <i class="user-icon icon-plus-fill mr8" />
                添加范围
              </bk-button>
              <template v-else>
                <bk-button theme="primary" text class="add-text">
                  已添加 <span>1</span> 个租户，<span>1</span>个组织，<span>2</span>个用户
                </bk-button>
                <ul class="add-list">
                  <li>
                    <i class="user-icon icon-homepage mr8"></i>
                    <span>租户</span>
                  </li>
                  <li>
                    <i class="bk-sq-icon icon-file-close mr8"></i>
                    <span>组织</span>
                  </li>
                  <li>
                    <i class="bk-sq-icon icon-personal-user mr8"></i>
                    <span>用户</span>
                  </li>
                </ul>
              </template>
            </div>
          </bk-form-item>
        </div>
        <div class="item-flex">
          <bk-form-item label="动态信任策略" description="动态信任策略">
            <bk-switcher v-model="state.openMFA" theme="primary" size="large" />
          </bk-form-item>
          <bk-form-item label="信任天数">
            <bk-radio-group v-model="state.days">
              <bk-radio-button
                v-for="item in state.daysList"
                :key="item.value"
                :label="item.name"
              />
            </bk-radio-group>
          </bk-form-item>
        </div>
        <bk-form-item label="" required>
          <div class="item-flex">
            <bk-checkbox>
              连续
            </bk-checkbox>
            <bk-input
              style="width: 85px;"
              type="number"
              behavior="simplicity"
              :min="0"
              :max="5"
            />
            <span class="text-sm/[32px]">天 未登录自动冻结（冻结后用户无法登录）</span>
          </div>
        </bk-form-item>
      </bk-form>
    </div>
    <div class="setting-btn">
      <bk-button theme="primary" class="mr8">保存</bk-button>
      <bk-button>重置</bk-button>
    </div>
    <!-- 添加范围 -->
    <bk-dialog
      width="640"
      height="520"
      class="department-dialog"
      :auto-close="false"
      :title="'添加启用范围'"
      :is-show="isShowSetDepartments"
      @confirm="selectDeConfirmFn"
      @closed="isShowSetDepartments = false">
      <div class="select-department-wrapper">
        <SetDepartment
          :initial-departments="[]" />
      </div>
    </bk-dialog>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { reactive, ref } from 'vue';

import SetDepartment from '@/components/set-department/SetDepartment.vue';

const isShow = ref(false);
const isShowSetDepartments = ref(false);
const getSelectedDepartments = ref([]);
const state = reactive({
  basicLogin: [
    { name: '账密登录（本地）', value: '1', default: false },
    { name: 'OpenLDAP登录', value: '2', default: false },
    { name: 'MAD登录', value: '3', default: false },
    { name: '企业微信登录', value: '4', default: false },
    { name: '手机号+验证码', value: '5', default: false },
    { name: '邮箱+验证码', value: '6', default: false },
  ],
  accountLogin: [
    { name: '微信', value: 'weixin' },
    { name: 'QQ', value: 'qq' },
    { name: 'Google', value: 'google' },
  ],
  openMFA: true,
  days: '3天',
  daysList: [
    { name: '3天', value: 3 },
    { name: '7天', value: 7 },
    { name: '14天', value: 14 },
    { name: '30天', value: 30 },
    { name: '60天', value: 60 },
  ],
});

const handleClickAdd = () => {
  isShowSetDepartments.value = true;
};

const selectDeConfirmFn = () => {
  if (!getSelectedDepartments.value.length) {
    Message({
      message: this.$t('请选择组织'),
      theme: 'warning',
    });
    return;
  }
};
</script>

<style lang="less" scoped>
.login-setting-content {
  height: calc(100vh - 104px);
  padding: 24px;

  .setting-item {
    margin-bottom: 16px;
    background: #fff;
    border-radius: 2px;
    box-shadow: 0 2px 4px 0 #1919290d;

    .item-title {
      padding: 16px 0 16px 24px;
      font-size: 14px;
      font-weight: 700;
    }

    .setting-form {
      margin-left: 64px;

      .item-flex {
        display: flex;

        .bk-form-item {
          width: 145px;

          .icon-plus-fill {
            font-size: 14px;
            color: #3a84ff;
          }

          &:first-child {
            width: 145px;
          }

          &:last-child {
            width: calc(100% - 145px);
          }
        }
      }

      ::v-deep .bk-form-item {
        &:last-child {
          padding-bottom: 24px;
          margin-bottom: 0;
        }
      }

      .add-wrapper {
        .bk-button {
          display: block;
          font-size: 14px;
          color: #3A84FF;
        }

        .add-text span {
          font-weight: 700;
        }

        .add-list {
          width: 320px;
          padding: 16px;
          background: #F5F7FA;
          border-radius: 2px;

          li {
            i {
              font-size: 16px;
              color: #A3C5FD;
            }

            span {
              font-size: 14px;
            }
          }
        }
      }
    }
  }

  .setting-btn {
    button {
      width: 88px;
    }
  }
}

.department-dialog {
  .select-department-wrapper {
    height: calc(100% - 7px);
  }

  .set-department-wrapper {
    width: 590px;
    height: 100%;
  }
}
</style>
