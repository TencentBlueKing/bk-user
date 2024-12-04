<template>
  <div v-clickoutside="handleClickOutside">
    <bk-dropdown
      class="mr-[16px]"
      trigger="manual"
      :is-show="dropdownVisible"
      @hide="() => (state.logoutDropdown = false)"
      @show="() => (state.logoutDropdown = true)">
      <bk-button @click="dropdownVisible = !dropdownVisible" :disabled="selectList.length === 0">
        <div :class="['help-info', { 'active-username': state.logoutDropdown }]">
          <span class="help-info-name"> {{ $t('批量操作') }}</span>
          <AngleDown class="angle-down-icon" />
        </div>
      </bk-button>
      <template #content>
        <bk-dropdown-menu>
          <bk-dropdown-item
            v-for="item in dropdownList"
            :key="item"
            :class="{ 'disabled': item.disabled }"
            v-bk-tooltips="{
              content: item.tips,
              disabled: !item.disabled
            }"
            @click.prevent="() => {
              if (item.disabled) return
              item.handle(item)
            }">
            {{ item.label}}
          </bk-dropdown-item>
        </bk-dropdown-menu>
      </template>
    </bk-dropdown>
    <!-- 批量重置密码弹框 -->
    <bk-dialog
      :width="500"
      :is-show="batchPasswordDialogShow"
      :title="$t('重置密码')"
      :theme="'primary'"
      :size="'normal'"
      :height="200"
      @closed="batchPasswordDialogShow = false"
      @confirm="resetBatchPasswordConfirm"
    >
      <bk-form
        form-type="vertical"
        ref="formRef"
        :model="formData">
        <bk-form-item :label="$t('新密码')" property="newPassword" required>
          <passwordInput
            v-model="formData.newPassword" :style="{ width: '80%' }" clearable
            :placeholder="passwordTips.join('、')"
            v-bk-tooltips="{ content: passwordTips.join('\n'), theme: 'light' }"
            @input="(val) => inputPassword(val, 'newPassword')" />
          <bk-button outline theme="primary" @click="randomPasswordHandle">{{$t('随机生成')}}</bk-button>
        </bk-form-item>
        <bk-form-item :label="$t('确认密码')" property="confirmPassword" required>
          <passwordInput
            :class="{ 'is-error': isError }"
            v-model="formData.confirmPassword"
            :placeholder="$t('请再次输入密码')"
            @input="(val) => inputPassword(val, 'confirmPassword')" />
          <div class="bk-form-error" v-show="isError">{{ $t('两次输入的密码不一致，请重新输入') }}</div>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
    <!-- 批量修改信息弹窗 -->
    <bk-dialog
      :width="500"
      :is-show="batchInfo"
      :title="$t('批量修改用户信息')"
      :theme="'primary'"
      :size="'normal'"
      :height="200"
      @closed="cancelBatchInfo"
      @confirm="confirmBatchInfo"
    >
      <bk-dropdown
        class="info-dropdown"
        :is-show="userInfoVisible"
        trigger="manual"
        :popover-options="{ width: '452' }">
        <bk-button class="mr-[24px] info-button" @click="userInfoVisible = !userInfoVisible">
          <i class="user-icon icon-add-2 mr8 text-[#3A84FF]" />
          <span class="text-[#3A84FF]"> {{ $t('新增批量修改字段') }}</span>
        </bk-button>
        <template #content>
          <bk-dropdown-menu>
            <bk-dropdown-item
              v-for="(item, index) in userInfoOptions"
              :key="index"
              :class="{ 'is-selected': item.selected, 'is-disabled': item.disabled }"
              @click.native="selectOption(item)"
            >
              {{ item.text }}
              <i v-if="item.selected" class="user-icon icon-check-line" />

            </bk-dropdown-item>
          </bk-dropdown-menu>
        </template>
      </bk-dropdown>
      <bk-form
        form-type="vertical"
        ref="infoFormRef"
        :model="infoFormData"
        :rules="rules">
        <bk-form-item v-if="selectedOption === 'date'" :label="$t('续期')">
          <bk-date-picker
            v-model="infoFormData.dateTime"
            type="date"
            :placeholder="$t('选择日期')"
            format="yyyy-MM-dd HH:mm:ss"
            append-to-body>
          </bk-date-picker>
        </bk-form-item>
        <bk-form-item v-if="selectedOption === 'leader'" :label="$t('直属上级')">
          <bk-select
            v-model="infoFormData.leader"
            filterable
            multiple
            :input-search="false"
            multiple-mode="tag"
            collapse-tags
            id-key="id">
            <bk-option
              v-for="item in leaderList"
              :key="item.id"
              :value="item.id"
              :name="`${item.username}(${item.full_name})`"
              :label="`${item.username}(${item.full_name})`">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <CustomFields v-if="selectedOption === 'custom'" :extras="infoFormData.customField" :rules="rules" />
      </bk-form>
    </bk-dialog>
  </div>
</template>


<script setup lang="ts">
import { clickoutside as vClickoutside, InfoBox, Message } from 'bkui-vue';
import { AngleDown } from 'bkui-vue/lib/icon';
import dayjs from 'dayjs';
import { computed, onMounted, reactive, ref, watch } from 'vue';

import CustomFields from '@/components/custom-fields/index.vue';
import passwordInput from '@/components/passwordInput.vue';
import { randomPasswords } from '@/http';
import { batchAccountExpired, batchCreate, batchCustomField, batchDeleteUser, batchLeader, batchResetPassword, batchUpdateStatus, optionalLeaderList, passwordRule } from '@/http/organizationFiles';
import { getFields } from '@/http/settingFiles';
import { t } from '@/language/index';
import useAppStore from '@/store/app';

const appStore = useAppStore();

const props = defineProps({
  selectList: {
    type: Array,
  },
  isEnabledPassword: {
    type: Boolean,
  },
});

/** 是否为本地数据源 */
const isLocalDataSource = computed(() => {
  return appStore.currentTenant?.data_source?.plugin_id === 'local';
});

const formData = ref({
  newPassword: '',
  confirmPassword: '',
});
const formRef = ref();
const state = reactive({
  logoutDropdown: false,
  helpDropdown: false,
  languageDropdown: false,
});;

const batchPasswordDialogShow = ref(false); // 修改密码弹窗
const batchInfo = ref(false); // 修改用户信息弹窗
const userInfoVisible = ref(false);
const selectedOption = ref();
const passwordTips = ref([]);
const isError = ref(false);
const extrasList = ref();
const infoFormData = ref({});
const leaderList = ref([]);
const rules = ref({});
const infoFormRef = ref();
const emits = defineEmits(['updateNode', 'addNode', 'deleteNode', 'moveOrg', 'reloadList']);

const dropdownVisible = ref(false);

const dropdownList = ref<any[]>([
  {
    label: t('移动至组织'),
    isShow: true,
    disabled: !isLocalDataSource.value,
    tips: t('非本地数据源，无法移动至组织'),
    confirmFn: batchCreate,
    handle: (item: any) => {
      emits('moveOrg', item);
    },
  },
  {
    label: t('重置密码'),
    key: 'password',
    disabled: !props.isEnabledPassword && !isLocalDataSource.value,
    tips: !props.isEnabledPassword ? t('当前租户未启用账密登录，无法修改密码') : !isLocalDataSource.value ? t('非本地数据源，无法重置密码') : '',
    handle: () => {
      const userIds = props.selectList.map(item => item.id);
      batchPasswordDialogShow.value = true;
      passwordRule(userIds[0]).then((res) => {
        passwordTips.value = res.data?.rule_tips;
      });
      formData.value = {
        newPassword: '',
        confirmPassword: '',
      };
    },
  },
  {
    label: t('修改用户信息'),
    key: 'userInfo',
    handle: () => {
      batchInfo.value = true;
    },
  },
  {
    label: t('启用'),
    key: 'enabled',
    handle: () => {
      confirmBatchAction('enable');
    },
  },
  {
    label: t('停用'),
    key: 'disabled',
    handle: () => {
      confirmBatchAction('disabled');
    },
  },
  {
    label: t('删除'),
    isShow: true,
    disabled: !isLocalDataSource.value,
    tips: t('非本地数据源，无法删除'),
    handle: () => {
      confirmBatchAction('delete');
    },
  },
]);

const userInfoOptions = ref([
  { text: t('续期'), type: 'date', selected: false, disabled: false },
  { text: t('直属上级'), type: 'leader', selected: false, disabled: !isLocalDataSource.value },
]);

onMounted(async () => {
  const [fieldsRes, leadersRes] = await Promise.all([
    getFields(),
    isLocalDataSource.value ? optionalLeaderList() : Promise.resolve([]),
  ]);
  extrasList.value = fieldsRes.data.custom_fields;
  extrasList.value.forEach((item) => {
    userInfoOptions.value.push({
      text: item.display_name,
      id: item.id,
      type: 'custom',
      selected: false,
    });
  });
  leaderList.value = leadersRes.data;
});

watch(infoFormData, (val) => {
  val?.customField?.forEach((item) => {
    val[item.name] = item.value;
  });
}, { deep: true, immediate: true });

const selectOption = (selectedItem) => {
  if (selectedItem.disabled) {
    userInfoVisible.value = false;
    return;
  }
  userInfoOptions.value.forEach(item => item.selected = false);
  selectedItem.selected = true;
  userInfoVisible.value = false;
  selectedOption.value = selectedItem.type;
  if (selectedItem.type === 'custom') {
    infoFormData.value.customField = [(extrasList.value.find(option => option.display_name === selectedItem.text))];
  }
};

const handleClickOutside = () => {
  setTimeout(() => {
    dropdownVisible.value = false;
  });
};

/**
   * 重置密码
  */
const inputPassword = (val: string, type) => {
  formData.value[type] = val;
  if (type === 'confirmPassword') isError.value = false;
};

/**
   * 生成随机密码
  */
const randomPasswordHandle = async (type: string) => {
  const res = await randomPasswords({ data_source_id: appStore.currentTenant.data_source.id });
  formData.value.newPassword = res.data?.password;
};

/**
   * 重置密码
   */
const resetBatchPasswordConfirm = async () => {
  try {
    await formRef.value.validate();
    if (formData.value.newPassword !== formData.value.confirmPassword) {
      return isError.value = true;
    }
    const userIds = props.selectList.map(item => item.id);
    const params = {
      user_ids: userIds,
      password: formData.value.newPassword,
    };
    await batchResetPassword(params);
    batchPasswordDialogShow.value = false;
    Message({ theme: 'success', message: t('重置密码成功') });
    emits('reloadList');
  } catch (e) {
    console.warn(e);
  }
};

const cancelBatchInfo = () => {
  userInfoVisible.value = false;
  batchInfo.value = false;
};

/**
 * 修改用户信息
 */
const confirmBatchInfo = () => {
  const userIds = props.selectList.map(item => item.id);
  const params = { user_ids: userIds };

  const actions = {
    date: () => {
      params.account_expired_at = dayjs(infoFormData.value.dateTime).format('YYYY-MM-DD HH:mm:ss');
      return batchAccountExpired(params);
    },
    leader: () => {
      params.leader_ids = infoFormData.value.leader;
      return batchLeader(params);
    },
    custom: async () => {
      await infoFormRef.value.validate();
      const {  name = '', value = null } = infoFormData.value.customField.length ? infoFormData.value.customField[0] : {};
      params.field_name = name;
      params.value = { [name]: value };
      return batchCustomField(params);
    },
  };

  const action = actions[selectedOption.value];

  if (action) {
    action().then(() => {
      batchInfo.value = false;
      selectedOption.value = '';
      userInfoOptions.value.forEach(item => item.selected = false);
      Message({ theme: 'success', message: t('更新成功') });
      emits('reloadList');
    });
  }
};

/**
 * 批量启用/停用/删除
 */
const confirmBatchAction = (actionType) => {
  const userIds = props.selectList.map(item => item.id);
  const actions = {
    enable: { title: t('确认批量启用所选用户 ？'), confirmText: t('启用'), params: { user_ids: userIds, status: 'enabled' } },
    disabled: { title: t('确认批量停用所选用户 ？'),  confirmText: t('停用'), params: { user_ids: userIds, status: 'disabled' } },
    delete: { title: t('确认批量删除用户？'),  confirmText: t('删除'), params: userIds?.join(',') },
  }[actionType];

  InfoBox({
    title: actions.title,
    theme: 'danger',
    confirmText: actions.confirmText,
    cancelText: t('取消'),
    onConfirm: () => {
      (async () => {
        await (actionType === 'delete'
          ? batchDeleteUser(actions.params)
          : batchUpdateStatus(actions.params));
        emits('reloadList');
      })();
    },
  });
};

</script>

<style lang="less" scoped>
.is-error {
  border-color: #ea3636;
}
:deep(.copy-icon) {
  right: 25px !important;
}
.info-dropdown {
  width: 100%;
  margin-bottom: 24px;
  .info-button {
    width: 100%;
    background: #F0F5FF;
    border: 1px solid #fff;
    &:hover {
      background: #E1ECFF;
    }
  }
}
.help-info {
  display: flex;
  align-items: center;
  .angle-down-icon {
    font-size: 22px;
    color: #979BA5;
  }
}
.active-username {
  cursor: pointer;
  .angle-down-icon {
    transform: rotate(180deg);
    transition: all 0.2s;
  }
}
.is-selected {
  color: #3A84ff !important;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.is-disabled {
  color: #c4c6cc !important;
  cursor: not-allowed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.icon-check-line {
  font-size: 14px
}

.disabled {
  color: #c4c6cc;
  cursor: not-allowed;
}
</style>
