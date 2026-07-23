<template>
  <div :class="['virtual-account-wrapper user-scroll-y', { 'has-alert': userStore.showAlert }]">
    <header>
      <div class="flex">
        <bk-button
          theme="primary"
          class="mr-[8px]"
          @click="handleClick('add')">
          <i class="user-icon icon-add-2 mr8" />
          {{ $t('新建') }}
        </bk-button>
      </div>
      <bk-input
        class="header-right"
        v-model="searchVal"
        :placeholder="$t('搜索用户名、全名')"
        type="search"
        clearable
        @enter="handleEnter"
        @clear="handleClear"
      />
    </header>
    <Table
      v-bkloading="{ loading: isLoading }"
      class="table-users"
      :max-height="maxHeight"
      :data="tableData"
      :pagination="pagination"
      :settings="settings"
      :show-settings="true"
      :virtual-y-config="{ enabled: true, gt: 10 }"
      @page-limit-change="pageLimitChange"
      @page-value-change="pageCurrentChange"
      @setting-change="handleSettingChange"
    >
      <template #empty>
        <Empty
          :type="curExceptionType"
          @clear="handleClear"
          @refresh="initVirtualUsers"
        />
      </template>
      <TableColumn
        field="username"
        :label="$t('用户名')"
        show-overflow="tooltip"
        :min-width="200"
      >
        <template #default="{ row }">
          <bk-button text theme="primary" @click="handleClick('view', row.id)">{{ row.username }}</bk-button>
        </template>
      </TableColumn>
      <TableColumn
        field="full_name"
        :label="$t('全名')"
        show-overflow="tooltip"
        :min-width="200"
      />
      <TableColumn
        field="app_codes"
        :label="$t('所属应用')"
        show-overflow="tooltip"
        :min-width="200"
      >
        <template #default="{ row }">
          {{ row.app_codes?.length ? row.app_codes?.join(', ') : '--' }}
        </template>
      </TableColumn>
      <TableColumn
        field="owners"
        :label="$t('账号责任人')"
        show-overflow="tooltip"
        :min-width="300"
      >
        <template #default="{ row }">
          <DisplayName :user-id="row.owners" />
        </template>
      </TableColumn>
      <TableColumn
        field="created_at"
        :label="$t('创建时间')"
        show-overflow="tooltip"
        :min-width="200"
      >
        <template #default="{ row }">
          <span>{{ row?.created_at || '--' }}</span>
        </template>
      </TableColumn>
      <TableColumn
        field="action"
        :label="$t('操作')"
        :min-width="160"
      >
        <template #default="{ row }">
          <bk-button class="mr-[8px]" theme="primary" text @click="handleClick('edit', row.id)">
            {{ $t('编辑') }}
          </bk-button>
        </template>
      </TableColumn>
    </Table>
    <!-- 新建编辑 -->
    <bk-sideslider
      :width="640"
      :is-show="detailsConfig.isShow"
      render-directive="if"
      :before-close="handleBeforeClose"
      quick-close
    >
      <template #header>
        <div class="flex justify-between w-full pr-[15px]">
          <div>{{ detailsConfig.title }}</div>
          <bk-button
            v-if="detailsConfig.type === 'view'"
            outline
            theme="primary"
            @click="handleClick('edit')">
            {{ $t('编辑') }}
          </bk-button>
        </div>
      </template>
      <EditDetails
        v-if="detailsConfig.type !== 'view'"
        :details-info="detailsInfo"
        @update-users="updateUsers"
        @handle-cancel-edit="handleCancelEdit" />
      <ViewDetails
        v-else
        :details-info="detailsInfo" />
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { inject, nextTick, onMounted, reactive, ref, watch  } from 'vue';

import { Table, TableColumn } from '@blueking/table';

import EditDetails from './EditDetails.vue';
import ViewDetails from './ViewDetails.vue';

import 'tippy.js/dist/tippy.css';
import 'tippy.js/themes/light.css';
import DisplayName from '@/components/display-name.vue';
import Empty from '@/components/SearchEmpty.vue';
import { useTableMaxHeight } from '@/hooks';
import useTableEmpty from '@/hooks/use-table-empty';
import { getVirtualUsers, getVirtualUsersDetail } from '@/http';
import { t } from '@/language/index';
import { useUser } from '@/store';

const userStore = useUser();
const maxHeight = useTableMaxHeight(148);

const editLeaveBefore = inject('editLeaveBefore');

const searchVal = ref('');
const isLoading = ref(false);
const tableData = ref([]);
const { setTypeToError, clearErrorType, curExceptionType } = useTableEmpty({
  filters: searchVal,
  clearTableData: () => {
    tableData.value = [];
  },
});

const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
  remote: true,
});

onMounted(() => {
  initVirtualUsers();
});

// 获取虚拟用户列表
const initVirtualUsers = async () => {
  try {
    isLoading.value = true;
    clearErrorType();

    const params = {
      page: pagination.current,
      pageSize: pagination.limit,
      keyword: searchVal.value,
    };
    const res = await getVirtualUsers(params);
    pagination.count = res.data?.count;
    tableData.value = res.data?.results;
  } catch (e) {
    console.warn(e);
    setTypeToError();
  } finally {
    isLoading.value = false;
  }
};

// 新建/编辑信息
const detailsInfo = ref({
  username: '',
  full_name: '',
  app_codes: '',
  owners: [],
});

// 侧栏配置
const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
});

const settings = reactive({
  checked: ['username', 'full_name', 'app_codes', 'owners', 'created_at', 'action'],
  size: 'small',
});

// 更改表格设置时，更新当前行高
const handleSettingChange = (data: any) => {
  settings.size = data.size as string;
};

const enumData = {
  add: {
    title: t('新建虚拟账户'),
    type: 'add',
  },
  view: {
    title: t('账号详情'),
    type: 'view',
  },
  edit: {
    title: t('编辑虚拟账户'),
    type: 'edit',
  },
};
const isViewToEdit = ref(false);
watch(() => detailsConfig.isShow, (val) => {
  if (!val) {
    nextTick(() => {
      detailsInfo.value = {
        username: '',
        full_name: '',
        app_codes: '',
        owners: [],
      };
      isViewToEdit.value = false;
    });
  }
});

const handleClick = async (type: string, id?: string) => {
  if (type !== 'add' && !isViewToEdit.value) {
    const res = await getVirtualUsersDetail(id);
    detailsInfo.value = res.data;
    detailsInfo.value.app_codes = res.data?.app_codes.join(',');
    if (type === 'view') {
      isViewToEdit.value = true;
    }
  }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

// 更新虚拟用户列表
const updateUsers = (message: string) => {
  detailsConfig.isShow = false;
  window.changeInput = false;
  Message({ theme: 'success', message });
  initVirtualUsers();
};

const handleCancelEdit = () => {
  window.changeInput = false;
  detailsConfig.isShow = false;
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    detailsConfig.isShow = !enableLeave;
  } else {
    detailsConfig.isShow = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};
const handleEnter = () => {
  pagination.current = 1;
  initVirtualUsers();
};

const handleClear = () => {
  searchVal.value = '';
  pagination.current = 1;
  initVirtualUsers();
};

const pageLimitChange = (limit: number) => {
  pagination.limit = limit;
  pagination.current = 1;
  initVirtualUsers();
};

const pageCurrentChange = (current: number) => {
  pagination.current = current;
  initVirtualUsers();
};
</script>

<style lang="less" scoped>
.has-alert {
  height: calc(100vh - 92px) !important;
}

.virtual-account-wrapper {
  height: calc(100vh - 52px);
  padding: 24px 160px;

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .header-right {
      width: 400px;
    }
  }

  .batch-operation {
    height: 32px;
    line-height: 32px;
    text-align: center;
    background-color: #F0F1F5;
    border: 1px dashed #AFB0B2;
  }

  ::v-deep .table-users .bk-table-footer {
    padding-left: 18px;
    background: #fff;
  }
}
</style>

<style lang="less">
/* 隐藏setting Tab的滚动条 */
.action-tab-wrapper {
  overflow-y: auto !important;
}
</style>
