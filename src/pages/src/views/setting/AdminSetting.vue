<template>
  <div class="admin-setting-wrapper">
    <div class="mb-[24px]" v-if="isEditAdminAccount">
      <bk-form
        ref="formRef"
        form-type="vertical"
        :model="formData"
        :rules="rules">
        <Row :title="$t('管理员账号')">
          <bk-form-item :label="$t('使用管理员账号登录')" required>
            <bk-switcher
              v-model="formData.status"
              theme="primary"
              size="large"
            />
          </bk-form-item>
          <div class="w-[544px]">
            <bk-form-item :label="$t('用户名')" property="username" required>
              <bk-input v-model="formData.username" :placeholder="validate.name.message" @focus="handleChange" />
            </bk-form-item>
            <bk-form-item :label="$t('密码')" property="password" required>
              <div class="flex justify-between">
                <bk-input
                  type="password"
                  v-model="formData.password" />
                <bk-button
                  outline
                  theme="primary"
                  class="ml-[8px] min-w-[88px]"
                  @click="handleRandomPassword">
                  {{ $t('随机生成') }}
                </bk-button>
              </div>
            </bk-form-item>
          </div>
        </Row>
      </bk-form>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        theme="primary"
        @click="saveAdminAccount"
      >
        {{ $t('保存') }}
      </bk-button>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        @click="isEditAdminAccount = false"
      >
        {{ $t('取消') }}
      </bk-button>
    </div>
    <Row v-else class="admin-setting-item" :title="$t('管理员账号')">
      <template #header>
        <bk-button
          class="min-w-[64px]"
          outline
          theme="primary"
          @click="editAdminAccount"
        >
          {{ $t('编辑') }}
        </bk-button>
      </template>
      <LabelContent :label="$t('状态')"></LabelContent>
      <LabelContent :label="$t('用户名')"></LabelContent>
      <LabelContent :label="$t('密码')"></LabelContent>
    </Row>

    <div class="mb-[24px]" v-if="isEditRealNameAccount">
      <Row class="admin-setting-item" :title="$t('实名账号')">
        <div class="flex items-center ml-[56px]">
          <bk-tag
            class="tag-style"
            v-for="(item, index) in selectedValue"
            :key="index"
            closable
            @close="handleTagClose">
            <template #icon>
              <i class="user-icon icon-yonghu" />
            </template>
            {{ item }}
          </bk-tag>
          <i class="user-icon icon-add-2"></i>
          <div>
            <bk-select
              v-model="selectedValue"
              class="w-[300px]"
              filterable
              multiple
              multiple-mode="tag"
            >
              <bk-option
                v-for="(item, index) in accounts"
                :id="item.value"
                :key="index"
                :name="item.label"
              />
            </bk-select>
          </div>
        </div>
      </Row>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        theme="primary"
        @click="saveRealNameAccount"
      >
        {{ $t('保存') }}
      </bk-button>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        @click="isEditRealNameAccount = false"
      >
        {{ $t('取消') }}
      </bk-button>
    </div>
    <Row v-else class="admin-setting-item" :title="$t('实名账号')">
      <template #header>
        <bk-button
          class="min-w-[64px]"
          outline
          theme="primary"
          @click="editRealNameAccount"
        >
          {{ $t('编辑') }}
        </bk-button>
      </template>
      <div class="ml-[56px]">
        <bk-tag
          class="tag-style"
          v-for="(item, index) in selectedValue"
          :key="index">
          <template #icon>
            <i class="user-icon icon-yonghu" />
          </template>
          {{ item }}
        </bk-tag>
      </div>
    </Row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import Row from '@/components/layouts/row.vue';
import { useValidate } from '@/hooks';
// import MemberSelector from '../tenant/MemberSelector.vue';

const validate = useValidate();

const selectedValue = ref(['dancing', 'bike']);

const accounts = ref([
  {
    value: 'climbing',
    label: '爬山',
  },
  {
    value: 'running',
    label: '跑步',
  },
  {
    value: 'unknow',
    label: '未知',
  },
  {
    value: 'fitness',
    label: '健身',
  },
  {
    value: 'bike',
    label: '骑车',
  },
  {
    value: 'dancing',
    label: '跳舞',
  },
  {
    value: 'sleep',
    label: '睡觉',
    disabled: true,
  },
]);

const formData = ref({
  status: true,
  username: 'admin',
  password: '12345678',
  managers: [],
});

const rules = {
  username: [validate.required, validate.userName],
  password: [validate.required],
};

const isEditAdminAccount = ref(false);

const editAdminAccount = () => {
  isEditAdminAccount.value = true;
};

const saveAdminAccount = () => {
  isEditAdminAccount.value = false;
};

const isEditRealNameAccount = ref(false);

const editRealNameAccount = () => {
  isEditRealNameAccount.value = true;
};
const saveRealNameAccount = () => {
  isEditRealNameAccount.value = false;
};
</script>

<style lang="less" scoped>
.admin-setting-wrapper {
  padding: 24px;

  .admin-setting-item {
    padding-bottom: 24px;

    ::v-deep .tag-style {
      height: 40px;
      line-height: 40px;

      .icon-yonghu {
        font-size: 21px;
        color: #C4C6CC;
      }

      .bk-tag-text {
        font-size: 16px;
        color: #313238;
      }

      .bk-tag-close {
        margin-left: 12px;
        font-size: 16px;
        color: #C4C6CC;
      }
    }

    .icon-add-2 {
      padding: 12px;
      font-size: 16px;
      color: #3A84FF;
      background: #F0F5FF;
      border-radius: 2px;

      &:hover {
        cursor: pointer;
        background: #E1ECFF;
      }
    }
  }
}
</style>
