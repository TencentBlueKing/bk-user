<template>
  <div class="data-source-wrapper">
    <MainBreadcrumbsDetails>
      <template #tag>
        <bk-tag>
          <template #icon>
            <i :class="typeText.icon" />
          </template>
          {{ typeText.name }}
        </bk-tag>
      </template>
    </MainBreadcrumbsDetails>
    <bk-form class="data-source-content user-scroll-y" form-type="vertical">
      <div class="content-item">
        <p class="item-title">基础信息</p>
        <bk-form-item label="数据源名称" required>
          <bk-input style="width: 560px;" v-model="data.name" />
        </bk-form-item>
        <bk-form-item label="" required>
          <bk-checkbox v-model="data.openLogin">
            开启账密登录
          </bk-checkbox>
        </bk-form-item>
      </div>
      <template v-if="data.openLogin">
        <div class="content-item">
          <p class="item-title">密码规则</p>
          <bk-form-item label="密码长度" required>
            <bk-input
              style="width: 200px;"
              type="number"
              suffix="至32位"
              v-model="data.passwordLength"
            />
          </bk-form-item>
          <bk-form-item label="密码必须包含" required>
            <bk-checkbox-group v-model="data.passwordMustIncludes">
              <bk-checkbox
                v-for="(item, index) in dataSourceConfig.passwordMustIncludes"
                :key="index"
                :label="item.value"
              >{{ item.label }}</bk-checkbox
              >
            </bk-checkbox-group>
          </bk-form-item>
          <bk-form-item label="">
            <div>
              <span>密码不允许连续</span>
              <bk-input
                style="width: 85px;"
                type="number"
                behavior="simplicity"
                v-model="data.passwordRultLength"
              />
              <span>位 出现</span>
            </div>
            <bk-checkbox-group v-model="data.excludeElementsConfig">
              <bk-checkbox
                v-for="(item, index) in dataSourceConfig.excludeElementsConfig"
                :key="index"
                :label="item.value"
              >{{ item.label }}</bk-checkbox
              >
            </bk-checkbox-group>
          </bk-form-item>
          <bk-form-item label="密码有效期" required>
            <bk-radio-group v-model="data.passwordValidDaysList">
              <bk-radio-button
                v-for="(item, index) in dataSourceConfig.passwordValidDaysList"
                :key="index"
                :label="item.days"
              >
                {{ item.text }}
              </bk-radio-button>
            </bk-radio-group>
          </bk-form-item>
          <bk-form-item label="密码试错次数" required>
            <bk-radio-group v-model="data.maxTrailTimesList">
              <bk-radio-button
                v-for="(item, index) in dataSourceConfig.maxTrailTimesList"
                :key="index"
                :label="item.times"
              >
                {{ item.text }}
              </bk-radio-button>
            </bk-radio-group>
          </bk-form-item>
          <bk-form-item label="锁定时间" required>
            <bk-input
              style="width: 200px;"
              type="number"
              suffix="秒"
              v-model="data.autoUnlockSeconds"
            />
          </bk-form-item>
        </div>
        <div class="content-item">
          <p class="item-title">初始密码设置</p>
          <bk-form-item label="" required>
            <bk-checkbox v-model="data.forceResetFirstLogin">
              首次登录强制修改密码
            </bk-checkbox>
          </bk-form-item>
          <bk-form-item label="" required>
            <div>
              <bk-checkbox v-model="data.forceResetFirstLogin">
                修改密码时不能重复前
              </bk-checkbox>
              <bk-input
                style="width: 85px;"
                type="number"
                behavior="simplicity"
              />
              <span>次 用过的密码</span>
            </div>
          </bk-form-item>
          <bk-form-item class="form-item-flex" label="密码生成方式" required>
            <bk-radio-group v-model="data.initPasswordMethod">
              <bk-radio label="random_via_mail">随机</bk-radio>
              <bk-radio label="fixed_preset">固定</bk-radio>
            </bk-radio-group>
            <bk-input
              class="input-password"
              v-if="data.initPasswordMethod === 'fixed_preset'"
              v-model="dataSourceConfig.fixedPassword"
              type="password"
            />
          </bk-form-item>
        </div>
        <div class="content-item">
          <p class="item-title">密码到期提醒</p>
          <bk-form-item label="提醒时间" required>
            <bk-checkbox-group v-model="data.noticeTime">
              <bk-checkbox
                v-for="(item, index) in dataSourceConfig.noticeTime"
                :key="index"
                :label="item.value"
              >{{ item.label }}</bk-checkbox
              >
            </bk-checkbox-group>
          </bk-form-item>
        </div>
      </template>
      <div class="btn">
        <bk-button theme="primary" class="mr8">提交</bk-button>
        <bk-button @click="handleClickCancel">取消</bk-button>
      </div>
    </bk-form>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import router from '@/router';

const route = useRoute();

// 当前面包屑展示文案
const typeText = computed(() => {
  switch (route.params.type) {
    case 'local':
      return {
        name: '本地',
        icon: 'user-icon icon-shujuku',
      };
  }
});

const data = reactive({
  name: '',
  openLogin: true,
  passwordLength: '',
  passwordRultLength: '',
  passwordMustIncludes: [],
  excludeElementsConfig: [],
  passwordValidDaysList: 30,
  maxTrailTimesList: 3,
  autoUnlockSeconds: '',
  forceResetFirstLogin: true,
  initPasswordMethod: '',
  noticeTime: [],
});

const dataSourceConfig = reactive({
  passwordMustIncludes: [
    { value: 'lower', label: '小写字母' },
    { value: 'upper', label: '大写字母' },
    { value: 'int', label: '数字' },
    { value: 'special', label: '特殊字符（除空格）' },
  ],
  excludeElementsConfig: [
    { value: 'keyboard_seq', label: '键盘序' },
    { value: 'alphabet_seq', label: '连续字母序' },
    { value: 'num_seq', label: '连续数字序' },
    { value: 'special_seq', label: '连续特殊符号序' },
    { value: 'duplicate_char', label: '重复字母、数字、特殊符号' },
  ],
  passwordValidDaysList: [
    { days: 30, text: '一个月' },
    { days: 90, text: '三个月' },
    { days: 180, text: '六个月' },
    { days: 365, text: '一年' },
    { days: -1, text: '永久' },
  ],
  maxTrailTimesList: [
    { times: 3, text: '3次' },
    { times: 5, text: '5次' },
    { times: 10, text: '10次' },
  ],
  forceResetFirstLogin: true,
  initPasswordMethod: 'fixed_preset',
  fixedPassword: '',
  noticeTime: [
    { value: 1, label: '1天' },
    { value: 7, label: '7天' },
    { value: 15, label: '15天' },
  ],
});

const handleClickCancel = () => {
  router.go(-1);
};
</script>

<style lang="less" scoped>
.data-source-wrapper {
  .data-source-content {
    height: calc(100vh - 104px);
    padding: 24px;

    .content-item {
      background: #fff;
      border-radius: 2px;
      box-shadow: 0 2px 4px 0 #1919290d;

      .item-title {
        padding: 16px 0 16px 24px;
        font-size: 14px;
        font-weight: 700;
      }

      :deep(.bk-form-item) {
        padding-bottom: 24px;
        margin-bottom: 0;
        margin-left: 64px;
        font-size: 14px;

        &:last-child {
          margin-bottom: 24px;
        }

        .bk-radio-button {
          width: 80px;

          .bk-radio-button-label {
            font-size: 14px !important;
          }
        }

        .bk-radio-label {
          font-size: 14px !important;
        }
      }

      .form-item-flex {
        :deep(.bk-form-content) {
          display: flex;

          .input-password {
            width: 240px;
            margin-left: 24px;
          }
        }
      }
    }

    .btn {
      button {
        width: 88px;
      }
    }
  }
}
</style>
