<template>
  <div class="login-setting-content user-scroll-y">
    <template v-if="isEdit">
      <div class="setting-item">
        <bk-form class="setting-form" form-type="vertical" v-model="state">
          <bk-form-item :label="$t('MFA认证方式')">
            <bk-checkbox-group v-model="state.methods">
              <bk-checkbox label="phone">{{ $t('手机号+验证码') }}</bk-checkbox>
              <bk-checkbox label="email">{{ $t('邮箱+验证码') }}</bk-checkbox>
            </bk-checkbox-group>
          </bk-form-item>
          <bk-form-item :label="$t('强制开启MFA')" :description="$t('强制开启MFA')">
            <bk-switcher v-model="state.openMFA" theme="primary" size="large" />
          </bk-form-item>
          <bk-form-item :label="$t('启用范围')">
            <div class="add-wrapper">
              <bk-button theme="primary" text v-if="!getSelectedDepartments.length" @click="handleClickAdd">
                <i class="user-icon icon-plus-fill mr8" />
                {{ $t('添加范围') }}
              </bk-button>
              <template v-else>
                <bk-button theme="primary" text class="add-text" @click="handleClickAdd">
                  {{ $t('已添加') }} <span>1</span> {{ $t('个租户') }}，
                  <span>1</span>{{ $t('个组织') }}，<span>2</span>{{ $t('个用户') }}
                </bk-button>
                <ul v-if="getSelectedDepartments.length" class="add-list">
                  <li class="selected-list" v-for="(item) in getSelectedDepartments" :key="item.id">
                    <div>
                      <i :class="getNodeIcon(item.type)" />
                      <span class="title">{{item.name}}</span>
                    </div>
                  </li>
                </ul>
              </template>
            </div>
          </bk-form-item>
          <div class="item-flex">
            <bk-form-item :label="$t('动态信任策略')" :description="$t('动态信任策略')">
              <bk-switcher v-model="state.openMFA" theme="primary" size="large" />
            </bk-form-item>
            <bk-form-item :label="$t('信任天数')">
              <bk-radio-group v-model="state.days">
                <bk-radio-button
                  class="min-w-[64px]"
                  v-for="(item, index) in state.daysList"
                  :key="index"
                  :label="item.value"
                >{{ item.name }}</bk-radio-button>
              </bk-radio-group>
            </bk-form-item>
          </div>
          <bk-form-item label="" required>
            <div class="item-flex">
              <bk-checkbox v-model="state.openMFA">
                {{ $t('连续') }}
              </bk-checkbox>
              <bk-input
                style="width: 85px;"
                type="number"
                behavior="simplicity"
                v-model="state.times"
                :min="0"
                :max="180"
              />
              <span class="text-sm/[32px]">{{ $t('天') }} {{ $t('未登录自动冻结（冻结后用户无法登录）') }}</span>
            </div>
          </bk-form-item>
        </bk-form>
      </div>
      <div class="setting-btn">
        <bk-button theme="primary" class="mr8" @click="handleClickSave">{{ $t('保存') }}</bk-button>
        <bk-button @click="handleClickCancel">{{ $t('取消') }}</bk-button>
      </div>
    </template>
    <template v-else>
      <div class="setting-item">
        <bk-button class="edit-btn" outline theme="primary" @click="handleClickEdit">
          {{ $t('编辑') }}
        </bk-button>
        <ul class="item-content">
          <li>
            <span class="key">{{ $t('MFA认证方式') }}：</span>
            <div>
              <bk-tag
                v-for="(item, index) in state.methods"
                :key="index">
                {{ item }}
              </bk-tag>
            </div>
          </li>
          <li>
            <span class="key">{{ $t('强制开启MFA') }}：</span>
            <span class="value" v-if="state.openMFA">
              <i class="user-icon icon-duihao-i"></i>
              {{ $t('已开启') }}
            </span>
            <span class="value" v-else>{{ $t('未开启') }}</span>
          </li>
          <li>
            <span class="key">{{ $t('启用范围') }}：</span>
            <div>
              <p>
                <span class="tenant">1</span>
                {{ $t('个租户') }}，<span class="department">1</span>
                {{ $t('个组织') }}，<span class="user">2</span>
                {{ $t('个用户') }}
              </p>
              <ul v-if="getSelectedDepartments.length" class="add-list mt-[8px]">
                <li class="selected-list" v-for="(item) in getSelectedDepartments" :key="item.id">
                  <div>
                    <i :class="getNodeIcon(item.type)" />
                    <span class="title">{{item.name}}</span>
                  </div>
                </li>
              </ul>
            </div>
          </li>
          <li>
            <span class="key">{{ $t('动态信任策略') }}：</span>
            <span class="value" v-if="state.openMFA">
              <i class="user-icon icon-duihao-i"></i>
              {{ $t('已开启') }}
            </span>
            <span class="value" v-else>{{ $t('未开启') }}</span>
          </li>
          <li>
            <span class="key">{{ $t('信任天数') }}：</span>
            <span class="value">{{ state.days }} {{ $t('天') }}</span>
          </li>
        </ul>
      </div>
    </template>
    <!-- 添加范围 -->
    <bk-dialog
      width="720"
      height="520"
      class="department-dialog"
      :quick-close="false"
      :title="$t('添加启用范围')"
      :is-show="isShowSetDepartments"
      @confirm="selectDeConfirmFn"
      @closed="isShowSetDepartments = false">
      <div class="select-department-wrapper">
        <SetDepartment
          :initial-departments="getSelectedDepartments"
          @select-list="selectList" />
      </div>
    </bk-dialog>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { reactive, ref } from 'vue';

import SetDepartment from '@/components/set-department/SetDepartment.vue';
import { t } from '@/language/index';
import { useMainViewStore } from '@/store';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const isEdit = ref(false);
const isShowSetDepartments = ref(false);
const getSelectedDepartments = ref([]);
const state = reactive({
  methods: ['phone', 'email'],
  openMFA: true,
  days: 3,
  daysList: [
    { name: `3 ${t('天')}`, value: 3 },
    { name: `7 ${t('天')}`, value: 7 },
    { name: `14 ${t('天')}`, value: 14 },
    { name: `30 ${t('天')}`, value: 30 },
    { name: `60 ${t('天')}`, value: 60 },
  ],
  times: 180,
});

const getNodeIcon = (type: string) => {
  switch (type) {
    case 'tenant':
      return 'user-icon icon-homepage';
    case 'department':
      return 'bk-sq-icon icon-file-close';
    default:
      return 'bk-sq-icon icon-personal-user';
  }
};

const handleClickEdit = () => {
  isEdit.value = true;
};

const handleClickCancel = () => {
  isEdit.value = false;
};

const handleClickSave = () => {
  isEdit.value = false;
};

const handleClickAdd = () => {
  isShowSetDepartments.value = true;
};

const selectDeConfirmFn = () => {
  if (!getSelectedDepartments.value.length) {
    Message({
      message: '请选择组织',
      theme: 'warning',
    });
    return;
  }

  isShowSetDepartments.value = false;
};

const selectList = (val) => {
  getSelectedDepartments.value = val;
};
</script>

<style lang="less" scoped>
.login-setting-content {
  height: calc(100vh - 104px);
  padding: 24px;

  .setting-item {
    position: relative;
    padding: 24px 40px;
    margin-bottom: 16px;
    background: #fff;
    border-radius: 2px;
    box-shadow: 0 2px 4px 0 #1919290d;

    .setting-form {
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
          padding-bottom: 8px;
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
      }
    }

    .add-list {
      width: 320px;
      padding: 8px 12px;
      background: #F5F7FA;
      border-radius: 2px;

      li {
        margin-bottom: 0 !important;
        line-height: 36px;

        div {
          display: flex;
          align-items: center;
          font-size: 14px;

          i {
            margin-right: 12px;
            font-size: 18px;
            color: #A3C5FD;
          }
        }
      }
    }

    .edit-btn {
      position: absolute;
      right: 40px;
      min-width: 64px;
    }

    .item-content {
      position: relative;
      width: 90%;

      li {
        display: flex;
        width: 100%;
        margin-bottom: 18px;
        font-size: 14px;

        &:last-child {
          margin-bottom: 0;
        }

        .key {
          display: inline-block;
          min-width: 110px;
          text-align: right;
        }

        .value {
          color: #313238;

          .user-icon {
            font-size: 20px;
            color: #2dcb56;
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
  ::v-deep .bk-modal-content {
    height: 422px !important;
    max-height: none;
    padding: 0 !important;
    overflow: hidden !important;

    .select-department-wrapper {
      height: 100%;

      .set-department-wrapper {
        width: 100%;
        height: 100%;
      }
    }
  }
}
</style>
