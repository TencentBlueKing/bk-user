<template>
  <div class="admin-setting-wrapper" v-bkloading="{ loading: isLoading }">
    <Row class="admin-setting-item" :title="$t('内置管理员')">
      <LabelContent :label="$t('状态')">
        <bk-tag :theme="adminAccount.enable_login ? 'success' : ''">
          {{ adminAccount.enable_login ? $t('启用') : $t('未启用') }}
        </bk-tag>
        <bk-button
          text
          theme="primary"
          @click="changeStatus"
          :disabled="adminAccount.enable_login && isDisabled"
          v-bk-tooltips="{ content: $t('唯一的管理员不能停用'), disabled: !adminAccount.enable_login || !isDisabled }">
          {{ adminAccount.enable_login ? $t('去停用') : $t('去启用') }}
        </bk-button>
      </LabelContent>
      <LabelContent :label="$t('用户名')">
        <template v-if="!isEditUsername">
          <span>{{ adminAccount.username }}</span>
          <i
            class="user-icon icon-edit edit"
            @click="editUsername" />
        </template>
        <template v-else>
          <bk-input
            class="username-input" style="width: 300px" v-model.trim="adminAccount.username" @enter="saveUsername" />
          <bk-button
            text
            theme="primary"
            class="ml-[12px] mr-[12px]"
            :disabled="!adminAccount.username"
            @click="saveUsername">
            {{ $t('确定') }}
          </bk-button>
          <bk-button text theme="primary" @click="cancelUsername">
            {{ $t('取消') }}
          </bk-button>
        </template>
      </LabelContent>
      <LabelContent :label="$t('密码')">
        <span>*************</span>
        <bk-button
          class="ml-[8px]"
          text
          theme="primary"
          @click="resetPasswordConfig.isShow = true"
        >
          <i class="user-icon icon-refresh mr-[6px]" />
          {{ $t('重置密码') }}
        </bk-button>
      </LabelContent>
    </Row>

    <div class="mb-[24px]">
      <Row class="admin-setting-item" :title="$t('租户管理员')">
        <div class="flex items-center flex-wrap ml-[56px]">
          <bk-tag
            class="tag-style"
            v-for="item in selectedValue"
            :key="item.id"
            :closable="item.isMouseenter"
            @mouseenter="item.isMouseenter = true"
            @mouseleave="item.isMouseenter = false"
            @close="deleteAccount(item.id)">
            <template #icon>
              <i class="user-icon icon-yonghu" />
            </template>
            <DisplayName :user-id="item.id" />
          </bk-tag>
          <i
            class="user-icon icon-add-2"
            v-if="!showSelectInput"
            @click="handleSelectValue" />
          <div v-else class="mb-[12px] flex">
            <UserSelector
              class="!w-[300px]"
              v-model:value="changeValues"
              :show-admin="false"
              :exclude-user-ids="selectedValue.map(item => item.id)" />
            <bk-button
              text
              theme="primary"
              class="ml-[16px] mr-[12px]"
              style="font-size: 14px"
              @click="saveRealUsers">
              {{ $t('确定') }}
            </bk-button>
            <bk-button text theme="primary" style="font-size: 14px" @click="cancelRealUsers">
              {{ $t('取消') }}
            </bk-button>
          </div>
        </div>
      </Row>
    </div>

    <!-- 重置密码 -->
    <ResetPasswordDialog
      v-model:is-show="resetPasswordConfig.isShow"
      :loading="resetPasswordConfig.isLoading"
      :show-password-tips="false"
      @confirm="handleConfirmPassword"
    />
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, InfoBox, Message  } from 'bkui-vue';
import { nextTick, onMounted, reactive, ref, watch } from 'vue';

import DisplayName from '@/components/display-name.vue';
import Row from '@/components/layouts/ItemRow.vue';
import LabelContent from '@/components/layouts/LabelContent.vue';
import ResetPasswordDialog from '@/components/ResetPasswordDialog.vue';
import UserSelector from '@/components/UserSelector.vue';
import {
  deleteRealManagers,
  getRealManagers,
  patchBuiltinManager,
  postRealManagers,
  putBuiltinManagerPassword,
} from '@/http';
import { t } from '@/language/index';
import { useMainViewStore, useUser } from '@/store';

const userStore = useUser();
const store = useMainViewStore();
store.customBreadcrumbs = false;

const adminAccount = ref({
  username: '',
  enable_login: false,
});
const fixedAdminAccount = ref({});
const isLoading = ref(false);

onMounted(() => {
  isLoading.value = true;
  initBuiltinManager();
  initRealManagers();
});

const initBuiltinManager = async () => {
  try {
    await userStore.initAdmin();
    adminAccount.value = userStore.admin;
    fixedAdminAccount.value = { ...userStore.admin };
  } catch (e) {
    isLoading.value = false;
    console.warn(e);
  }
};

// 修改管理员账号状态
const changeStatus = () => {
  InfoBox({
    width: 400,
    infoType: adminAccount.value.enable_login ? 'warning' : undefined,
    title: adminAccount.value.enable_login ? t('是否停用管理员账号？') : t('是否启用管理员账号？'),
    subTitle: adminAccount.value.enable_login
      ? t('停用后，将不可使用管理员账号进行登录')
      : t('启用后，可使用管理员账号进行登录'),
    confirmText: adminAccount.value.enable_login ? t('停用') : t('启用'),
    theme: adminAccount.value.enable_login ? 'danger' : undefined,
    onConfirm: () => {
      patchBuiltinManager({ enable_login: !adminAccount.value.enable_login }).then(() => {
        initBuiltinManager();
        const message = adminAccount.value.enable_login ? t('停用成功') : t('启用成功');
        Message({ theme: 'success', message });
      })
        .catch((error) => {
          console.warn(error);
        });
    },
  });
};

// 修改用户名
const isEditUsername = ref(false);

watch(() => isEditUsername.value, (val) => {
  window.changeInput = val;
}, {
  deep: true,
});

const saveUsername = async () => {
  if (!adminAccount.value.username) return;
  await patchBuiltinManager({ username: adminAccount.value.username });
  isEditUsername.value = false;
  Message({ theme: 'success', message: t('保存成功') });
};

const cancelUsername = () => {
  adminAccount.value.username = fixedAdminAccount.value?.username;
  isEditUsername.value = false;
};

const editUsername = () => {
  isEditUsername.value = true;
  nextTick(() => {
    const usernameInput = document.querySelectorAll('.username-input input');
    usernameInput[0].focus();
  });
};

// 重置密码
const resetPasswordConfig = reactive({
  isShow: false,
  isLoading: false,
  password: '',
  confirmPassword: '',
});

const handleConfirmPassword = async (password: string) => {
  try {
    resetPasswordConfig.isLoading = true;
    await putBuiltinManagerPassword({ password });
    resetPasswordConfig.isShow = false;
    Message({ theme: 'success', message: t('密码重置成功') });
  } catch (e) {
    console.warn(e);
  } finally {
    resetPasswordConfig.isLoading = false;
  }
};

// 实名管理员信息
const selectedValue = ref([]);

const isDisabled = ref(false);
const initRealManagers = async () => {
  try {
    const res = await getRealManagers();
    selectedValue.value = res.data;
    isDisabled.value = !selectedValue.value.length;
  } finally {
    isLoading.value = false;
  }
};

const showSelectInput = ref(false);

watch(() => showSelectInput.value, (val) => {
  window.changeInput = val;
}, {
  deep: true,
});

const handleSelectValue = async () => {
  showSelectInput.value = true;
};

const changeValues = ref([]);

// 删除实名管理员
const deleteAccount = (id: string) => {
  deleteRealManagers(id).then(() => {
    initRealManagers();
  });
};

const saveRealUsers = () => {
  showSelectInput.value = false;
  if (!Object.keys(changeValues.value).length) return;
  selectedValue.value = [];
  postRealManagers({
    ids: changeValues.value,
  }).then(() => {
    changeValues.value = [];
    initRealManagers();
  });
};

const cancelRealUsers = () => {
  changeValues.value = [];
  showSelectInput.value = false;
};
</script>

<style lang="less" scoped>
.admin-setting-wrapper {
  padding: 24px;

  .admin-setting-item {
    padding-bottom: 24px;

    ::v-deep .tag-style {
      height: 40px;
      margin: 0 12px 12px 0;
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
        margin-right: 10px;
        font-size: 16px;
        color: #979BA5;
      }
    }

    .icon-add-2 {
      padding: 12px;
      margin: 0 12px 12px 0;
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

.edit {
  margin-left: 8px;
  color: #979BA5;

  &:hover {
    color: #3A84FF;
    cursor: pointer;
  }
}
</style>
