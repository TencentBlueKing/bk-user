<template>
  <div class="admin-setting-wrapper">
    <Row class="admin-setting-item" :title="$t('管理员账号')">
      <LabelContent :label="$t('状态')">
        <bk-tag :theme="adminAccount.enable_account_password_login ? 'success' : ''">
          {{ adminAccount.enable_account_password_login ? $t('启用') : $t('未启用') }}
        </bk-tag>
        <bk-button text theme="primary" @click="changeStatus">
          {{ adminAccount.enable_account_password_login ? $t('去停用') : $t('去启用') }}
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
          <bk-input class="username-input" style="width: 300px" v-model="adminAccount.username" />
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
          <i class="user-icon icon-refresh" />
          {{ $t('重置密码') }}
        </bk-button>
      </LabelContent>
    </Row>

    <div class="mb-[24px]">
      <Row class="admin-setting-item" :title="$t('实名账号')">
        <div class="flex items-center flex-wrap ml-[56px]">
          <bk-tag
            class="tag-style"
            v-for="item in selectedValue"
            :key="item.id"
            :closable="!showSelectInput"
            @close="deleteAccount(item.id)">
            <template #icon>
              <i class="user-icon icon-yonghu" />
            </template>
            {{ `${item.username}（${item.full_name}）` }}
          </bk-tag>
          <i
            class="user-icon icon-add-2"
            v-if="!showSelectInput"
            @click="handleSelectValue" />
          <div v-else class="mb-[12px] flex">
            <MemberSelector
              class="w-[300px]"
              :state="realUsers"
              :params="params"
              @changeSelectList="changeSelectList"
              @searchUserList="fetchRealUsers"
              @scrollChange="scrollChange"
            />
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
    <bk-dialog
      :is-show="resetPasswordConfig.isShow"
      :title="resetPasswordConfig.title"
      :is-loading="resetPasswordConfig.isLoading"
      :theme="'primary'"
      :quick-close="false"
      :height="200"
      @closed="closedPassword"
      @confirm="confirmPassword"
    >
      <bk-form
        class="mt-[8px]"
        ref="formRef"
        form-type="vertical"
        :model="resetPasswordConfig"
        :rules="rules">
        <bk-form-item :label="$t('密码')" property="password" required>
          <div class="flex justify-between">
            <bk-input
              type="password"
              v-model="resetPasswordConfig.password"
              @change="changePassword" />
            <bk-button
              outline
              theme="primary"
              class="ml-[8px] min-w-[88px]"
              @click="handleRandomPassword">
              {{ $t('随机生成') }}
            </bk-button>
          </div>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </div>
</template>

<script setup lang="ts">
import { InfoBox, Message } from 'bkui-vue';
import { nextTick, onMounted, reactive, ref, watch } from 'vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import Row from '@/components/layouts/row.vue';
import MemberSelector from '@/components/MemberSelector.vue';
import { useValidate } from '@/hooks';
import {
  getBuiltinManager,
  getRealManagers,
  getRealUsers,
  patchBuiltinManager,
  putBuiltinManagerPassword,
  postRealManagers,
  deleteRealManagers,
  randomPasswords,
} from '@/http';
import { t } from '@/language/index';

const validate = useValidate();

const adminAccount = ref({
  username: '',
  enable_account_password_login: false,
});
const fixedAdminAccount = ref({});

onMounted(() => {
  initBuiltinManager();
  initRealManagers();
});

const initBuiltinManager = async () => {
  const { data } = await getBuiltinManager();
  adminAccount.value = data;
  fixedAdminAccount.value = { ...data };
};

// 修改管理员账号状态
const changeStatus = () => {
  InfoBox({
    width: 400,
    infoType: adminAccount.value.enable_account_password_login ? 'warning' : undefined,
    title: t(adminAccount.value.enable_account_password_login ? '是否停用管理员账号？' : '是否启用管理员账号？'),
    subTitle: t(adminAccount.value.enable_account_password_login
      ? '停用后，将不可使用管理员账号进行登录'
      : '停用后，可使用管理员账号进行登录'),
    confirmText: adminAccount.value.enable_account_password_login ? t('停用') : undefined,
    theme: adminAccount.value.enable_account_password_login ? 'danger' : undefined,
    onConfirm: async () => {
      await patchBuiltinManager({ enable_account_password_login: !adminAccount.value.enable_account_password_login });
      initBuiltinManager();
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
  await patchBuiltinManager({ username: adminAccount.value.username });
  isEditUsername.value = false;
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
  title: t('重置密码'),
  isLoading: false,
  password: '',
});

const formRef = ref();

const rules = {
  password: [validate.required],
};

const closedPassword = () => {
  resetPasswordConfig.isShow = false;
  resetPasswordConfig.password = '';
};

const changePassword = (val: string) => {
  resetPasswordConfig.password = val;
};

// 随机密码
const handleRandomPassword = async () => {
  try {
    const passwordRes = await randomPasswords({});
    resetPasswordConfig.password = passwordRes.data.password;
  } catch (e) {
    console.warn(e);
  }
};

const confirmPassword = async () => {
  try {
    await formRef.value.validate();
    resetPasswordConfig.isLoading = true;

    await putBuiltinManagerPassword({ password: resetPasswordConfig.password });
    resetPasswordConfig.isShow = false;
    resetPasswordConfig.password = '';
    Message({ theme: 'success', message: t('密码重置成功') });
  } catch (e) {
    console.warn(e);
  } finally {
    resetPasswordConfig.isLoading = false;
  }
};

// 实名账号信息
const selectedValue = ref([]);

const realUsers = ref({
  count: 0,
  results: [],
});

const params = reactive({
  page: 1,
  pageSize: 10,
  keyword: '',
  exclude_manager: true,
});

const initRealManagers = async () => {
  const res = await getRealManagers();
  selectedValue.value = res.data;
};

const showSelectInput = ref(false);

watch(() => showSelectInput.value, (val) => {
  window.changeInput = val;
}, {
  deep: true,
});

const handleSelectValue = async () => {
  showSelectInput.value = true;
  const res = await getRealUsers({
    exclude_manager: params.exclude_manager,
  });
  realUsers.value = res.data;
};

const changeValues = ref([]);
const changeSelectList = (values: string[]) => {
  changeValues.value = values;
};

// 获取用户列表
const fetchRealUsers = (value: string) => {
  params.keyword = value;
  params.page = 1;
  getRealUsers(params).then((res) => {
    realUsers.value = res.data;
  });
};

const scrollChange = () => {
  params.page += 1;
  getRealUsers(params).then((res) => {
    realUsers.value.count = res.data.count;
    realUsers.value.results.push(...res.data.results);
  });
};

// 删除实名账号
const deleteAccount = (id: string) => {
  deleteRealManagers(id).then(() => {
    initRealManagers();
  });
};

const saveRealUsers = () => {
  showSelectInput.value = false;
  selectedValue.value = [];
  postRealManagers({
    ids: changeValues.value,
  }).then(() => {
    initRealManagers();
  });
};

const cancelRealUsers = () => {
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
        margin-left: 12px;
        font-size: 16px;
        color: #C4C6CC;
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
