<template>
  <div class="organization-table px-[24px] py-[24px]">
    <div class="table-search mb-[16px]">
      <bk-button
        v-if="!isCollaborativeUsers
          && isTenantStatus
          && organizationStore.isConfiguredLocalSource"
        class="mr-[16px] button-upload"
        @click="importDialogHandle"
      >
        <Upload class="mr-[8px] text-[16px] icon-upload" />
        {{ $t('导入') }}
      </bk-button>
      <bk-button
        v-if="isShowBtn"
        theme="primary"
        class="mr-[10px]"
        @click="fastInputDialogShow = true"
      >
        <i class="user-icon icon-add-2 mr8" />
        {{ $t('快速录入') }}
      </bk-button>
      <bk-button
        v-if="isShowBtn"
        class="mr-[16px]"
        @click="handleGetUsersDialog">
        {{ $t('拉取已有用户') }}
      </bk-button>
      <batchOperation
        :select-list="selectList"
        @move-org="batchMoveOrg"
        @reload-list="handleAfterBatchOperation"
      />
      <bk-checkbox
        class="h-[32px] ml-[2px]"
        :label="$t('仅显示本级用户')"
        v-model="recursive"
        @change="reloadList"
      />
      <bk-searchSelect
        class="header-right"
        v-model="keyword"
        :data="searchSelectOptions"
        :placeholder="
          createPlaceholder({
            type: 'searchSelect',
            labels: ['用户名', '姓名', '账号状态', '邮箱', '手机号'],
          })
        "
        unique-select
        value-behavior="need-key"
      >
      </bk-searchSelect>
    </div>
    <Table
      ref="tableRef"
      :max-height="curTableMaxHeight"
      class="organization-table-main"
      :data="tableData"
      :pagination="pagination"
      v-bkloading="{ loading: isLoading }"
      :virtual-y-config="{ enabled: true, gt: 10 }"
      @checkbox-change="handleSelectTable"
      @checkbox-all="handleSelectAll"
      @page-limit-change="pageLimitChange"
      @page-value-change="pageCurrentChange"
    >
      <template #empty>
        <Empty
          :type="curExceptionType"
          @clear="handleClear"
          @refresh="reloadList"
        />
      </template>
      <template #prepend v-if="selectList.length > 0 && !isCollaborativeUsers">
        <div class="table-total">
          <span>{{ $t('当前已选择')}} <b>{{selectList.length}}</b> {{ $t('条数据，可以批量')}}</span>
          <bk-button
            text
            class="table-operate ml-[12px]"
            :disabled="isSelectedNotLocalSource"
            v-bk-tooltips="{
              content: $t('非本地数据源，无法移动至组织'),
              disabled: !isSelectedNotLocalSource
            }"
            @click="handleBatchRemoveFromOrg">
            {{$t('移出当前组织')}}
          </bk-button>
          <bk-button
            text
            class="table-operate ml-[12px]"
            :disabled="isSelectedNotLocalSource"
            v-bk-tooltips="{
              content: $t('非本地数据源，无法移动至组织'),
              disabled: !isSelectedNotLocalSource
            }"
            @click="handleBatchAppendOrg">
            {{$t('追加目标组织')}}
          </bk-button>
          <bk-button
            text
            class="table-operate ml-[12px]"
            :disabled="isSelectedNotLocalSource"
            v-bk-tooltips="{
              content: $t('非本地数据源，无法移动至组织'),
              disabled: !isSelectedNotLocalSource
            }"
            @click="handleBatchReplaceOrg">
            {{$t('清空并加入组织')}}
          </bk-button>
        </div>
      </template>
      <!-- 本地数据源才可操作 -->
      <TableColumn
        v-if="tableData.length > 0 && organizationStore.isConfiguredLocalSource"
        fixed="left"
        type="checkbox"
        width="50"
      />
      <TableColumn
        field="username"
        :label="$t('用户名')"
        show-overflow-tooltip
      >
        <template #default="{ row }">
          <span
            class="table-operate"
            @click="editInfoHandle(row)"
          >
            {{ row?.username || '--' }}
          </span>
        </template>
      </TableColumn>
      <TableColumn
        field="full_name"
        :label="$t('姓名')"
      />
      <TableColumn
        field="status"
        :label="$t('账号状态')"
      >
        <template #default="{ row }">
          <span class="status-main">
            <label :class="['status-label', row?.status]"></label>
            {{ statusEnum?.[row?.status] || '--' }}
          </span>
        </template>
      </TableColumn>
      <TableColumn
        field="email"
        :label="$t('邮箱')"
      />
      <TableColumn
        field="phone"
        :label="$t('手机号')"
      >
        <template #default="{ row }">
          <span>{{ row.phone ? `(+${row.phone_country_code}) ${row.phone}` : row.phone }}</span>
        </template>
      </TableColumn>
      <TableColumn
        field="departments"
        :label="$t('所属组织')"
      >
        <template #default="{ row }">
          <bk-popover
            :disabled="row.departments?.length === 0"
            render-type="auto"
            theme="dark"
          >
            <template #content>
              <div
                v-bkloading="{
                  loading: isOrgPathLoading && row?.organization_paths?.length !== 0,
                  size: 'small',
                  theme: 'primary',
                }"
                class="min-w-[30px]"
              >
                <div
                  v-for="(path, index) in (row?.organization_paths || [])"
                  :key="index"
                >
                  {{ path }}
                </div>
              </div>
            </template>
            <span @mouseenter="handleHoverOrg(row)">
              {{ (row.departments || []).join('、') || '--' }}
            </span>
          </bk-popover>
        </template>
      </TableColumn>
      <TableColumn
        v-if="!isCollaborativeUsers"
        field="operation"
        :label="$t('操作')"
      >
        <template #default="{ row, $rowIndex }: any">
          <span v-if="row.data_source_id === organizationStore.localSourceId">
            <label class="table-operate" @click="editInfoHandle(row, true)">{{ $t('编辑') }}</label>
            <bk-popover
              ext-cls="operate-popover"
              :ref="(el: PopoverInstanceType) => setItemRef(el, `dropdownRef${$rowIndex}`)"
              theme="light"
              trigger="click"
              :arrow="false"
              placement="bottom"
            >
              <i class="inline-block user-icon icon-more ml8" />
              <template #content>
                <div class="operate-menu-list">
                  <bk-button
                    text
                    class="operate-button-item"
                    @click="onToggleUserStatusClick(row, $rowIndex)"
                  >
                    {{ row.status === 'enabled' ? $t('停用') : $t('启用') }}
                  </bk-button>
                  <bk-button
                    text
                    class="operate-button-item"
                    :disabled="!organizationStore.getDataSourceInfo(row.data_source_id).enable_password"
                    v-bk-tooltips="{
                      content: $t('当前数据源未启用账密登录，无法重置密码'),
                      disabled: organizationStore.getDataSourceInfo(row.data_source_id).enable_password
                    }"
                    @click="onResetPasswordClick(row, $rowIndex)"
                  >
                    {{ $t('重置密码') }}
                  </bk-button>
                  <bk-button
                    text
                    class="operate-button-item"
                    @click="onDeleteUserClick(row, $rowIndex)"
                  >
                    {{ $t('删除') }}
                  </bk-button>
                </div>
              </template>
            </bk-popover>
          </span>
          <label
            v-else
            class="table-operate"
            @click="onToggleUserStatusClick(row)"
          >
            {{ row.status === 'enabled' ? $t('停用') : $t('启用') }}
          </label>
        </template>
      </TableColumn>
    </Table>
  </div>
  <!-- 拉取已有用户 -->
  <bk-dialog
    :is-show="getUsersDialogShow"
    :title="$t('拉取已有用户')"
    :theme="'primary'"
    :size="'normal'"
    @closed="() => getUsersDialogShow = false"
    @confirm="confirmGetUser"
  >
    <bk-select
      v-model="getUsersValue"
      class="user-select-main"
      :list="getUserList"
      filterable
      multiple
      auto-focus
      :clearable="false"
      id-key="id"
      multiple-mode="tag"
      display-key="username"
      :remote-method="remoteMethod"
    >
      <template #optionRender="{ item }">
        <div class="user-info-option pt-[5px] pb-[5px]">
          <DisplayName :user-id="item.id" class="text-[#313238]" />
          <p class="text-[#979BA5] mt-[6px]">
            <bk-overflow-title
              :style="{ display: 'inline-block' }"
              class="text-[#979BA5] leading-[20px]"
              :class="{
                'w-[370px]': !!item.organization_paths.length,
                'w-[270px]': !!(item.organization_paths.length && item.status === 'disabled')
              }"
            >
              {{ item.organization_paths[0] }}
            </bk-overflow-title>
            <bk-tag
              v-if="item.organization_paths.length > 1"
              theme="info"
              class="inline-block !m-0 h-[20px] !ml-[2px]"
              v-bk-tooltips="{
                content: item.organization_paths.join('\n'),
                placement: 'right',
                extCls: 'tag-tool-tips',
              }"
            >
              +{{ item.organization_paths.length }}
            </bk-tag>
          </p>
        </div>
      </template>
    </bk-select>
  </bk-dialog>
  <!-- 移动至组织/添加至组织弹框 -->
  <bk-dialog
    :is-show="moveDialogShow"
    :title="dialogTitle"
    :theme="'primary'"
    :size="'normal'"
    @closed="moveDialogShow = false"
    @confirm="confirmOperations"
  >
    <div class="mb-[16px] text-[#979BA5]">
      {{ moveTips }}
    </div>
    <bk-form
      class="example"
      form-type="vertical"
    >
      <bk-form-item :label="$t('选择组织')">
        <bk-select
          v-model="selectedValue"
          class="bk-select"
          filterable
          multiple
          auto-focus
          :clearable="false"
          id-key="id"
          display-key="name"
          collapse-tags
        >
          <bk-option
            v-for="item in dataSource"
            :key="item.id"
            :disabled="chooseDepartments.includes(item.name)"
            v-bk-tooltips="{
              content: $t('已在当前部门'),
              disabled: !chooseDepartments.includes(item.name),
              boundary: 'parent'
            }"
            :value="item.id"
            :name="item.name"
            :label="item.name" />
        </bk-select>
      </bk-form-item>
    </bk-form>
  </bk-dialog>
  <!-- 重置密码弹框 -->
  <bk-dialog
    :width="500"
    :is-show="passwordDialogShow"
    :title="$t('重置密码')"
    :theme="'primary'"
    :size="'normal'"
    :height="200"
    @closed="resetPasswordClose"
  >
    <bk-loading :loading="isResetPasswordLoading">
      <bk-form
        class="example"
        form-type="vertical"
      >
        <bk-form-item :label="$t('新密码')" required>
          <passwordInput
            v-model="password"
            v-bk-tooltips="{
              content: passwordTips.join('\n'),
              theme: 'light',
            }"
            clearable
            :style="{ width: '80%' }"
            :placeholder="passwordTips.join('、')"
          />
          <bk-button
            outline
            theme="primary"
            @click="randomPasswordHandle">
            {{$t('随机生成')}}
          </bk-button>
        </bk-form-item>
      </bk-form>
    </bk-loading>
    <template #footer>
      <div class="flex justify-end">
        <bk-button
          theme="primary"
          class="mr-[8px]"
          @click="resetPasswordConfirm"
          :disabled="isResetPasswordLoading">
          {{ t('确定') }}
        </bk-button>
        <bk-button @click="resetPasswordClose">
          {{ t('取消') }}
        </bk-button>
      </div>
    </template>
  </bk-dialog>
  <!-- 快速录入弹框 -->
  <FastInputDialog
    v-model:is-show="fastInputDialogShow"
    @click-import="importDialogHandle"
    @success="fastInputSuccess" />
  <!-- 编辑用户 -->
  <bk-sideslider
    :width="640"
    :is-show="editDetailsShow"
    :title="isDetailSlider ? $t('编辑用户') : $t('用户详情')"
    :before-close="handleBeforeClose"
    render-directive="if"
    quick-close
    transfer
  >
    <template #header>
      <div class="w-full">{{isDetailSlider ? $t('编辑用户') : $t('用户详情')}}</div>
      <bk-button
        v-if="!isDetailSlider && !isCollaborativeUsers && isLocalDataSource"
        class="mr-[20px]"
        @click="editInfoHandle(editDetailsInfo, true)">
        {{$t('编辑')}}
      </bk-button>
    </template>
    <EditDetails
      v-if="isDetailSlider"
      :details-info="editDetailsInfo"
      :data-source-id="detailsInfo.data_source_id"
      @update-users="updateUsers"
      @handle-cancel-edit="handleBeforeClose" />
    <ViewUser
      v-else
      :user-data="detailsInfo"
      :detail="editDetailsInfo"
      :is-show-btn="!isCollaborativeUsers && (isLocalDataSource || isLdapDataSource)"
      @update-users="updateUsers"
    />
  </bk-sideslider>
  <!-- 导入弹框 -->
  <ImportDialog
    v-model:is-show="importDialogShow"
    :data-source-id="organizationStore.localSourceId"
    @success="reloadList"
  />
</template>

<script setup lang="tsx">
import { InfoBox, Message } from 'bkui-vue';
import { Upload } from 'bkui-vue/lib/icon';
import { PopoverInstanceType } from 'bkui-vue/lib/select/type';
import { computed, inject, reactive, ref, watch } from 'vue';

import { Table, TableColumn } from '@blueking/table';

import ViewUser from '../details/ViewUser.vue';

import batchOperation from './batch-operation.vue';
import EditDetails from './edit-detail.vue';
import FastInputDialog from './fast-input-dialog.vue';

import DisplayName from '@/components/display-name.vue';
import ImportDialog from '@/components/import-dialog/import-dialog.vue';
import passwordInput from '@/components/passwordInput.vue';
import Empty from '@/components/SearchEmpty.vue';
import { useTableMaxHeight } from '@/hooks';
import useTableEmpty from '@/hooks/use-table-empty';
import { useSearchPlaceholder } from '@/hooks/useSearchPlaceholder';
import { randomPasswords } from '@/http';
import {
  batchCreate,
  batchDelete,
  batchDelUpdate,
  delTenantsUser,
  getOrganizationPaths,
  getTenantsUserDetail,
  getTenantsUserList,
  getUsersList,
  optionalDepartmentsList,
  passwordRule,
  resetTenantsUserPassword,
  updateTenantsUserStatus,
} from '@/http/organizationFiles';
import { getFields } from '@/http/settingFiles';
import { TenantsUserItemData } from '@/http/types/organizationFiles';
import { t } from '@/language/index';
import useOrganizationStore from '@/store/organization';

const { createPlaceholder } = useSearchPlaceholder();
const curTableMaxHeight = useTableMaxHeight(200);
const organizationStore = useOrganizationStore();

/** searchSelect下拉框数据 */
const searchSelectOptions = [
  {
    name: t('用户名'),
    id: 'username',
  },
  {
    name: t('姓名'),
    id: 'full_name',
  },
  {
    name: t('账号状态'),
    id: 'status',
    children: [
      {
        name: t('正常'),
        id: 'enabled',
      },
      {
        name: t('停用'),
        id: 'disabled',
      },
      {
        name: t('冻结'),
        id: 'expired',
      },
    ],
  },
  {
    name: t('邮箱'),
    id: 'email',
  },
  {
    name: t('手机号'),
    id: 'phone',
  },
];

const recursive = ref(true);
const isLoading = ref(false);
const editLeaveBefore = inject('editLeaveBefore');
const editDetailsShow = ref(false);
const dropdownRefs = ref<Record<string, PopoverInstanceType>>({});

const keyword = ref([]);
const { setTypeToError, clearErrorType, curExceptionType } = useTableEmpty({
  filters: keyword,
});
const selectedValue = ref([]);
const isDetailSlider = ref(false);
const moveTips = ref('');
const tableRef = ref();
const detailsInfo = ref<TenantsUserItemData>({} as TenantsUserItemData);
const selectList = ref([]);
const password = ref('');
const dataSource = ref([]);
const moveDialogShow = ref(false);
const currentHandle = ref({});
const dialogTitle = ref('');
const passwordDialogShow = ref(false);
const fastInputDialogShow = ref(false);
const importDialogShow = ref(false);
const editDetailsInfo = ref({});
const getUsersDialogShow = ref(false);
const getUsersValue = ref([]);
const getUserList = ref([]);
const chooseDepartments = ref([]);
const passwordTips = ref([]);
const isOrgPathLoading = ref(false);
const pagination = reactive({
  count: 0,
  limit: 10,
  current: 1,
  remote: true,
});

const statusEnum = reactive<Record<string, string>>({
  enabled: t('正常'),
  disabled: t('停用'),
  expired: t('冻结'),
});
const tableData = ref<TenantsUserItemData[]>([]);
const isResetPasswordLoading = ref(false);

/** 是否为租户层级 */
const isTenantStatus = computed(() => organizationStore.curSelectedTenant === 'current' && organizationStore.curSelectedType === 'tenant');
/** 是否为协同租户 */
const isCollaborativeUsers = computed(() => organizationStore.curSelectedTenant === 'collaboration');

const searchSelectFilters = computed(() => {
  const result: Record<string, string> = {};
  for (const item of keyword.value) {
    result[item.id] = item.values[0].id;
  }
  return result;
});
  /** 当前选中的是否为本地数据源 */
const isLocalDataSource = computed(() => (organizationStore.curSelectedDataSource?.plugin_id === 'local'));
/** 当前选中的是否为 LDAP 数据源 */
const isLdapDataSource = computed(() => (organizationStore.curSelectedDataSource?.plugin_id === 'ldap'));
/**
   * 是否展示
   *  - 快速录入
   *  - 拉取已有用户
   * @description 不为协同租户 && 不为租户层级 && 为本地数据源
   */
const isShowBtn = computed(() => (
  !isCollaborativeUsers.value
    && !isTenantStatus.value
    && organizationStore.selectedOrg?.dataSourceId === organizationStore.localSourceId));

/** 当前选中的是否包含非本地数据源 */
// eslint-disable-next-line max-len
const isSelectedNotLocalSource = computed(() => selectList.value.some(item => item.data_source_id !== organizationStore.localSourceId));

// 停用/启用用户点击事件
const onToggleUserStatusClick = (row: TenantsUserItemData, index?: number) => {
  detailsInfo.value = row;
  if (index !== undefined) {
    dropdownRefs.value[`dropdownRef${index}`]?.hide();
  }
  const isEnabled = row.status === 'enabled';
  InfoBox({
    title: isEnabled ? t(`确定停用用户${detailsInfo.value.full_name} ？`) : t(`确定启用用户${detailsInfo.value.full_name} ？`),
    subTitle: isEnabled ? t('停用后，用户将无法登录') : t('启用后，用户将恢复登录'),
    infoType: 'warning',
    theme: 'danger',
    onConfirm: async () => {
      await updateTenantsUserStatus(row.id);
      reloadList();
    },
  });
};

// 重置密码点击事件
const onResetPasswordClick = (row: TenantsUserItemData, index: number) => {
  detailsInfo.value = row;
  dropdownRefs.value[`dropdownRef${index}`]?.hide();
  passwordDialogShow.value = true;
  passwordRule(detailsInfo.value.id).then((res) => {
    passwordTips.value = res.data?.rule_tips;
  });
};

// 删除用户点击事件
const onDeleteUserClick = (row: TenantsUserItemData, index: number) => {
  detailsInfo.value = row;
  dropdownRefs.value[`dropdownRef${index}`]?.hide();
  InfoBox({
    title: t(`确认删除用户：${detailsInfo.value.username}？`),
    subTitle: t('删除后，用户将被彻底删除，无法恢复'),
    theme: 'danger',
    infoType: 'warning',
    onConfirm: async () => {
      await delTenantsUser(detailsInfo.value.id);
      reloadList();
    },
  });
};

const editInfoHandle = async (row: TenantsUserItemData, isDetail = false) => {
  isDetailSlider.value = isDetail;
  detailsInfo.value = row;
  const [useRes, fieldsRes] = await Promise.all([
    getTenantsUserDetail(row.id),
    getFields(),
  ]);
  const { data } = useRes;
  const extrasList = fieldsRes.data.custom_fields;
  extrasList.map(item => item.value = data.extras[item.name]);
  Object.assign(data, {
    department_ids: getIdList(data?.departments),
    leader_ids: getIdList(data?.leaders),
    extras: extrasList,
  });
  editDetailsInfo.value = data;
  editDetailsShow.value = true;
  window.changeInput = false;
};

// 批量移出当前组织
const handleBatchRemoveFromOrg = () => {
  currentHandle.value = { confirmFn: null };
  InfoBox({
    title: `${t('确认将选中的用户移出')}${organizationStore.selectedOrg.deptName}`,
    onConfirm: async () => {
      const params = {
        user_ids: getBatchUserIds(true),
        source_department_id: organizationStore.selectedOrg.deptId,
      };
      await batchDelete(params);
      moveDialogShow.value = false;
      reloadList();
    },
  });
};

// 批量追加目标组织
const handleBatchAppendOrg = () => {
  currentHandle.value = { confirmFn: batchCreate };
  dialogTitle.value = t('追加目标组织');
  handleOperations(t('将'), t('追加到以下组织'));
};

// 批量清空并加入组织
const handleBatchReplaceOrg = () => {
  currentHandle.value = { confirmFn: batchDelUpdate };
  dialogTitle.value = t('清空并加入组织');
  handleOperations(t('清空'), t('的现有组织，并加入到以下组织'));
};

/**
 * 拉取已有用户
 * @description 由于仅支持本地数据源拉取已有用户，因此直接使用organizationStore.localSourceId
 */
const getUserListFun = async (keyword = '') => {
  const res = await getUsersList({
    tenant_id: organizationStore.selectedOrg.tenantId,
    keyword,
    data_source_id: organizationStore.localSourceId,
  });
  getUserList.value = res.data;
};

/** 点击拉取已有用户按钮 */
const handleGetUsersDialog = () => {
  getUsersValue.value = [];
  getUsersDialogShow.value = true;
  getUserList.value = [];
  getUserListFun();
};

const remoteMethod = (word = '') => {
  // 当字符大于1或等于0时，才拉取用户列表（为0时用于清空时恢复原来的列表）
  if (word.length > 1 || word.length === 0) {
    getUserListFun(word);
  }
};

/** 确认拉取已有用户 */
const confirmGetUser = async () => {
  try {
    const param = {
      target_department_ids: [organizationStore.selectedOrg.deptId],
      user_ids: getUsersValue.value,
    };
    await batchCreate(param);
    getUsersDialogShow.value = false;
    Message({ theme: 'success', message: t('拉取已有用户成功') });
    handleClear();
  } finally {
    isLoading.value = false;
  }
};

const getBatchUserIds = (isArray = false) => {
  const userId = [];
  selectList.value.map(item => userId.push(item.id));
  if (isArray) {
    return userId.join(',');
  }
  return userId;
};

/** 点击移动/移动至组织按钮 */
const handleOperations = async (prefix: string, suffix: string) => {
  chooseDepartments.value = [];
  moveDialogShow.value = true;
  selectedValue.value = [];
  dataSource.value = [];
  const users = [];
  selectList.value.map((item) => {
    chooseDepartments.value.push(...item.departments);
    users.push(item.full_name);
  });
  const isMore = users.length > 3;
  const showStr = isMore ? `...${t('等')}${users.length}${t('个用户')}` : '';
  moveTips.value = `${prefix}${users.slice(0, 3).join('、')}${showStr}${suffix}`;
  // 这里直接使用organizationStore.localSourceId 因为只有本地数据源支持移动组织
  const res = await optionalDepartmentsList({ data_source_id: organizationStore.localSourceId });
  dataSource.value = res.data;
};

const confirmOperations = async () => {
  const params = {
    user_ids: getBatchUserIds(),
    target_department_ids: selectedValue.value,
  };
  await currentHandle.value.confirmFn(params);
  moveDialogShow.value = false;
  handleClear();
};

const handleHoverOrg = (row) => {
  if (!row?.organization_paths) {
    const currentIndex = tableData.value.findIndex(item => item === row);
    isOrgPathLoading.value = true;
    getOrganizationPaths(row.id).then((res) => {
      const organization_paths = res?.data?.organization_paths;
      tableData.value[currentIndex].organization_paths  = organization_paths;
    })
      .finally(() => isOrgPathLoading.value = false);
  }
};

const initTenantsUserList = async () => {
  try {
    tableData.value = [];
    selectList.value = [];
    isLoading.value = true;
    const params = {
      ...searchSelectFilters.value,
      page: pagination.current,
      page_size: pagination.limit,
      department_id: organizationStore.selectedOrg.deptId,
      recursive: !recursive.value,
    };
    const res = await getTenantsUserList(organizationStore.selectedOrg.tenantId, params);
    pagination.count = res.data?.count;
    tableData.value = res.data?.results;
    clearErrorType();
  } catch (e) {
    console.warn(e);
    setTypeToError();
  } finally {
    isLoading.value = false;
  }
};

const setItemRef = (el: PopoverInstanceType, key: string) => {
  if (el) {
    dropdownRefs.value[key] = el;
  }
};

/**
 * 生成随机密码
 * @description 仅本地数据源可以重置密码，直接使用organizationStore.localSourceId
 */
const randomPasswordHandle = async () => {
  const res = await randomPasswords({ data_source_id: organizationStore.localSourceId });
  password.value = res.data?.password;
};

/** 重置密码 */
const resetPasswordConfirm = async () => {
  try {
    isResetPasswordLoading.value = true;
    const param = { password: password.value };
    await resetTenantsUserPassword(detailsInfo.value.id, param);
    handleClear();
    resetPasswordClose();
    Message({ theme: 'success', message: t('重置密码成功') });
  } catch (e) {
    console.warn(e);
  } finally {
    isResetPasswordLoading.value = false;
  }
};

/** 取消重置密码 */
const resetPasswordClose = () => {
  passwordDialogShow.value = false;
  password.value = '';
};

const fastInputSuccess = () => {
  fastInputDialogShow.value = false;
  handleClear();
};

const handleClear = () => {
  keyword.value = [];
  reloadList();
};
  // 勾选数据行
const handleSelectTable = ({ row, checked }: { row: TenantsUserItemData; checked: boolean; }) => {
  checked ? selectList.value.push(row) : selectList.value = selectList.value.filter(item => item.id !== row.id);
};

// 勾选所有数据行
const handleSelectAll = ({ checked, records: data }: { checked: boolean; records: TenantsUserItemData[]}) => {
  selectList.value = checked ? data : [];
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
  }
  editDetailsShow.value = !enableLeave;
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};

// 更新虚拟用户列表
const updateUsers = (message: string) => {
  editDetailsShow.value = false;
  window.changeInput = false;
  Message({ theme: 'success', message });
  handleClear();
};

const handleAfterBatchOperation = () => {
  tableRef.value?.getVxeTableInstance()?.clearCheckboxRow();
  reloadList();
};

const reloadList = () => {
  pagination.current = 1;
  initTenantsUserList();
};

const pageLimitChange = (limit: number) => {
  pagination.limit = limit;
  reloadList();
};

const pageCurrentChange = (current: number) => {
  pagination.current = current;
  initTenantsUserList();
};

const getIdList = (data, key = 'id') => {
  if (!Array.isArray(data)) {
    return;
  }
  const values = data.reduce((acc, obj) => {
    if (key in obj) {
      acc.push(obj[key]);
    }
    return acc;
  }, []);
  return values;
};

const importDialogHandle = () => importDialogShow.value = true;

const batchMoveOrg = (params) => {
  currentHandle.value = params;
  dialogTitle.value = t('移动至组织');
  handleOperations(t('将'), t('从当前组织移出，并追加到以下组织'));
};

watch(
  keyword,
  () => {
    pagination.current = 1;
    initTenantsUserList();
  },
  {
    deep: true,
  },
);

watch(
  () => organizationStore.selectedOrg.deptId,
  () => {
    reloadList();
  },
);

</script>

<style lang="less">
.operate-popover {
  padding: 5px 0 !important;
}

.organization-table-main {
  transition: height 0.5s ease;
  .bk-table-head thead th {
    &:first-child {
      text-align: center;
    }
  }
}

.organization-table {
  height: 100%;

  .table-search {
    position: relative;
    display: flex;
    width: 100%;

    .button-upload:hover {
      border-color: #3A84ff;

      .icon-upload {
        color: #3A84ff;
      }
    }

    .header-right {
      position: absolute;
      right: 0;
      width: 30%;
      min-width: 400px;
    }
  }

  .organization-table-main {
    background: #fff;

    .table-total {
      width: 100%;
      height: 32px;
      line-height: 32px;
      color: #63656E;
      text-align: center;
      background: #F0F1F5;
    }

    .icon-more {
      display: inline-block;
      width: 24px;
      height: 24px;
      margin-left: 8px;
      font-size: 16px;
      line-height: 24px;
      cursor: pointer;

      &:hover {
        background: #F0F1F5;
        border-radius: 50%;
      }
    }

    .table-operate {
      color: #3A84FF;
      cursor: pointer;

      &.is-disabled {
        color: #c4c6cc;
        cursor: not-allowed;
      }
    }

    .status-label {
      position: relative;
      top: 2px;
      display: inline-block;
      width: 13px;
      height: 13px;
      margin-right: 3px;
      background: #3fc06d29;
      border-radius: 50%;

      &::before {
        position: absolute;
        top: 50%;
        left: 50%;
        display: inline-block;
        width: 7px;
        height: 7px;
        background: #3FC06D;
        border-radius: 50%;
        content: '';
        transform: translate(-50%, -50%);
      }

      &.disabled {
        background: #979ba529;

        &::before {
          background: #979BA5;
        }
      }
    }

    .operate-menu-list {
      display: flex;
      flex-direction: column;
      gap: 0;

      .operate-button-item {
        display: block;
        width: 100%;
        height: 32px;
        padding: 0 12px;
        line-height: 32px;
        color: #63656E;
        text-align: left;
        border-radius: 0;

        &:hover {
          background: #F5F7FA;
        }

        &.is-disabled {
          color: #c4c6cc;
        }
      }
    }
  }
}

.user-info-option {
  &.disabled {
    color: #c4c6cc;
    cursor: not-allowed;
  }
}
.tag-tool-tips {
  z-index: 99999 !important;
}

.operate-menu-list {
  display: flex;
  flex-direction: column;
  gap: 0;

  .operate-button-item {
    display: block;
    width: 100%;
    height: 32px;
    padding: 0 12px;
    line-height: 32px;
    color: #63656E;
    text-align: left;
    border-radius: 0;

    &:hover {
      background: #F5F7FA;
    }

    &.is-disabled {
      color: #c4c6cc;
    }
  }
}
</style>
<style lang="less" scoped>
:deep(.copy-icon) {
  right: 25px !important;
}
</style>
