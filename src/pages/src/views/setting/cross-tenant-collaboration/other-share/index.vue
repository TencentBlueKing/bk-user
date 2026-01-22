<template>
  <div
    v-bkloading="{ loading: isLoading, zIndex: 10 }"
    :class="['user-info-wrapper user-scroll-y', { 'has-alert': userStore.showAlert }]">
    <header class="flex justify-end">
      <bk-button text theme="primary" @click="showUpdateRecord">
        <i class="user-icon icon-lishijilu" />
        {{ $t('数据更新记录') }}
      </bk-button>
    </header>
    <Table
      class="user-info-table"
      :data="tableData"
      :border="'outer'"
      :max-height="tableMaxHeight"
      :row-class="tableRowClassName"
      @filter-change="handleFilterChange"
    >
      <template #empty>
        <Empty
          :is-data-empty="isDataEmpty"
          :is-data-error="isDataError"
          :is-search-empty="isSearchEmpty"
          @handle-update="fetchFromStrategies"
          @handle-empty="handleClearFilter"
        />
      </template>
      <TableColumn
        field="source_tenant_id"
        :label="$t('源租户')"
        show-overflow="tooltip"
        :min-width="120"
      >
        <template #default="{ row }">
          <span>
            {{ row.source_tenant_id }}
          </span>
        </template>
      </TableColumn>
      <TableColumn
        field="target_status"
        :label="$t('状态')"
        show-overflow="tooltip"
        filter-multiple
        :filters="statusFilters"
        :min-width="120"
      >
        <template #default="{ row }">
          <div>
            <img :src="dataSourceStatus[row.target_status]?.icon" class="account-status-icon" />
            <span>{{ dataSourceStatus[row.target_status]?.text }}</span>
          </div>
        </template>
      </TableColumn>
      <TableColumn
        field="updated_at"
        :label="$t('更新时间')"
        show-overflow="tooltip"
        :min-width="160"
      />
      <TableColumn
        field="enable_status"
        :label="$t('启/停')"
        show-overflow="tooltip"
        filter-multiple
        :filters="enableFilters"
        :min-width="120"
      >
        <template #default="{ row }">
          <bk-switcher
            theme="primary"
            size="small"
            :value="row.target_status === 'enabled'"
            :disabled="row.target_status === 'unconfirmed'"
            @change="handleChange(row)"
          />
        </template>
      </TableColumn>
      <TableColumn
        field="action"
        :label="$t('操作')"
        :width="120"
      >
        <template #default="{ row }">
          <bk-button
            v-if="row.target_status === 'unconfirmed'"
            text
            theme="primary"
            @click="handleDetails(row, 'edit')"
          >
            {{ $t('去确认') }}
          </bk-button>
          <bk-button
            v-else
            text
            theme="primary"
            @click="handleDetails(row, 'view')"
          >
            {{ $t('查看详情') }}
          </bk-button>
        </template>
      </TableColumn>
    </Table>
    <!-- 侧边栏 -->
    <bk-sideslider
      :width="960"
      quick-close
      :is-show="detailsConfig.isShow"
      :title="detailsConfig.title"
      :before-close="handleBeforeClose"
    >
      <OperationDetails :config="detailsConfig" @update-list="updateList" @cancel="detailsConfig.isShow = false" />
    </bk-sideslider>
    <!-- 数据更新记录 -->
    <bk-sideslider
      width="960"
      class="update-record-dialog"
      dialog-type="show"
      :title="$t('数据更新记录')"
      :is-show="dialogConfig.isShow"
      @closed="dialogConfig.isShow = false"
      render-directive
      quick-close
      trensfer>
      <Table
        v-bkloading="{ loading: dialogConfig.loading, zIndex: 10 }"
        class="update-record-table"
        :data="dialogConfig.list"
        :border="'outer'"
        :pagination="pagination"
        :expand-config="expandConfig"
        @filter-change="dataRecordFilter"
        @page-limit-change="pageLimitChange"
        @page-value-change="pageCurrentChange"
        @row-expand="handleRowExpand"
      >
        <template #empty>
          <Empty
            :is-data-empty="dialogConfig.isDataEmpty"
            :is-data-error="dialogConfig.isDataError"
            :is-search-empty="dialogConfig.isDataSearch"
            @handle-update="fetchUpdateRecord"
            @handle-empty="handleClearRecordFilter"
          />
        </template>
        <TableColumn type="expand" :min-width="60">
          <template #content="{ row }">
            <div class="expand-wrapper">
              <div
                v-if="
                  row?.deletedObjs?.user_count ||
                    row?.deletedObjs?.department_count
                "
                class="expand-item">
                <span class="w-[40px] text-[#EA3636]">{{ $t('删除') }}:</span>
                <div class="expand-item-content">
                  <div class="content-users">
                    <i class="bk-sq-icon icon-personal-user" />
                    <div class="flex">
                      <span v-if="row?.deletedObjs?.user_count">
                        <span
                          v-for="(item, index) in row?.deletedObjs?.usernames"
                          :key="index">
                          <bk-tag class="mb-2">{{ item }}</bk-tag>
                        </span>
                        <tag v-if="row?.deletedObjs?.user_count > 50" style="color: #63656e;">
                          ... {{$t('共') + row?.deletedObjs?.user_count + $t('个用户')}}
                        </tag>
                      </span>
                      <tag v-else>--</tag>
                    </div>
                  </div>
                  <div class="content-departments">
                    <i class="bk-sq-icon icon-file-close" />
                    <div class="flex">
                      <span v-if="row?.deletedObjs?.department_count">
                        <span
                          v-for="(item, index) in row?.deletedObjs?.department_names"
                          :key="index">
                          <bk-tag class="mb-2">{{ item }}</bk-tag>
                        </span>
                        <tag v-if="row?.deletedObjs?.department_count > 50" style="color: #63656e;">
                          ... {{$t('共') + row?.deletedObjs?.department_count + $t('个部门')}}
                        </tag>
                      </span>
                      <tag v-else>--</tag>
                    </div>
                  </div>
                </div>
              </div>
              <div
                v-if="row?.createdObjs?.user_count ||
                  row?.createdObjs?.department_count"
                class="expand-item box-border">
                <div class="w-[40px] text-[#2DCB56]">{{ $t('新增') }}:</div>
                <div class="expand-item-content">
                  <div class="content-users">
                    <i class="bk-sq-icon icon-personal-user" />
                    <div class="flex">
                      <span v-if="row?.createdObjs?.user_count">
                        <span
                          v-for="(item, index) in row?.createdObjs?.usernames"
                          :key="index">
                          <bk-tag class="mb-2">{{ item }}</bk-tag>
                        </span>
                        <tag v-if="row?.createdObjs?.user_count > 50" style="color: #63656e;">
                          ... {{$t('共') + row?.createdObjs?.user_count + $t('个用户')}}
                        </tag>
                      </span>
                      <tag v-else>--</tag>
                    </div>
                  </div>
                  <div class="content-departments">
                    <i class="bk-sq-icon icon-file-close" />
                    <div class="flex">
                      <span v-if="row?.createdObjs?.department_count">
                        <span
                          v-for="(item, index) in row?.createdObjs?.department_names"
                          :key="index">
                          <bk-tag class="mb-2">{{ item }}</bk-tag>
                        </span>
                        <tag v-if="row?.createdObjs?.department_count > 50" style="color: #63656e;">
                          ... {{$t('共') + row?.createdObjs?.department_count + $t('个部门')}}
                        </tag>
                      </span>
                      <tag v-else>--</tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </TableColumn>
        <TableColumn
          field="start_at"
          :label="$t('时间')"
          show-overflow="tooltip"
          :width="160" />
        <TableColumn
          field="source_tenant_name"
          :label="$t('源租户')"
          show-overflow="tooltip"
          :width="120" />
        <TableColumn
          field="content"
          :label="$t('更新内容')"
          show-overflow="tooltip"
          :width="350">
          <template #default="{ row }">
            <bk-tag theme="danger">
              {{ $t('删除') }}：
              <i class="bk-sq-icon icon-personal-user" />
              <span>{{ row.content?.delete?.user }}</span>
              <i class="bk-sq-icon icon-file-close" />
              <span>{{ row.content?.delete?.department }}</span>
            </bk-tag>
            <bk-tag theme="success">
              {{ $t('新增') }}：
              <i class="bk-sq-icon icon-personal-user" />
              <span>{{ row.content?.create?.user }}</span>
              <i class="bk-sq-icon icon-file-close" />
              <span>{{ row.content?.create?.department }}</span>
            </bk-tag>
          </template>
        </TableColumn>
        <TableColumn
          field="status"
          :label="$t('状态')"
          show-overflow="tooltip"
          filter-multiple
          :filters="updateStatusFilters"
          :min-width="105">
          <template #default="{ row }">
            <img :src="dataRecordStatus[row.status]?.icon" class="account-status-icon" />
            <span>{{ dataRecordStatus[row.status]?.text }}</span>
          </template>
        </TableColumn>
        <TableColumn field="action" :label="$t('操作')" :min-width="105">
          <template #default="{ row }">
            <bk-button
              text
              theme="primary"
              style="margin-right: 8px;"
              @click="handleLogDetails(row)"
            >
              {{ $t('日志详情') }}
            </bk-button>
            <ExclamationCircleShape
              class="circle-shape"
              v-if="row.has_warning"
              v-bk-tooltips="{ content: t('有部分数据失败') }" />
          </template>
        </TableColumn>
      </Table>
    </bk-sideslider>
    <!-- 日志详情 -->
    <bk-sideslider
      ext-cls="log-wrapper"
      :is-show="logConfig.isShow"
      :title="$t('日志详情')"
      :width="800"
      quick-close
      :before-close="beforeClose"
      transfer
    >
      <template #header>
        <div class="logs-header">
          <span>{{ $t('日志详情') }}</span>
          <bk-tag>{{ logsDetails.start_at }}</bk-tag>
          <bk-tag :theme="dataRecordStatus[logsDetails.status]?.theme">
            {{ dataRecordStatus[logsDetails.status]?.text }}
          </bk-tag>
          <span class="logs-duration">{{ $t('总耗时') }} {{ durationText(logsDetails.duration) }}</span>
        </div>
      </template>
      <template #default>
        <SQLFile
          v-model="logsDetails.logs"
          readonly
          :title="$t('执行日志')" />
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { ExclamationCircleShape } from 'bkui-vue/lib/icon';
import { inject, reactive, ref, watchEffect } from 'vue';

import { Table, TableColumn } from '@blueking/table';

import OperationDetails from './OperationDetails.vue';

import Empty from '@/components/SearchEmpty.vue';
import SQLFile from '@/components/sql-file/SQLFile.vue';
import { useTableMaxHeight } from '@/hooks';
import { getCollaborationSyncRecords, getCollaborationSyncRecordsLogs, getFromStrategies, putFromStrategiesStatus } from '@/http';
import { t } from '@/language/index';
import { useMainViewStore, useUser } from '@/store';
import { dataRecordStatus, dataSourceStatus, durationText } from '@/utils';

const props = defineProps({
  active: {
    type: String,
    default: '',
  },
});
const store = useMainViewStore();
store.customBreadcrumbs = false;
const userStore = useUser();

const tableMaxHeight = useTableMaxHeight(238);
const editLeaveBefore = inject('editLeaveBefore');
const isLoading = ref(false);
const tableData = ref([]);
const originalTableData = ref([]); // 保存原始数据副本
const isDataEmpty = ref(false);
const isDataError = ref(false);
const isSearchEmpty = ref(false);

const statusFilters = ref([
  { label: t('正常'), value: 'enabled' },
  { label: t('未启用'), value: 'disabled' },
  { label: t('待确认'), value: 'unconfirmed' },
]);

const enableFilters = ref([
  { label: t('启用'), value: 'enabled' },
  { label: t('停用'), value: 'disabled' },
]);

const handleFilterChange = ({ field, values }: { field: any; values: string[] }) => {
  // 如果没有筛选条件，恢复原始数据
  if (values.length === 0) {
    isSearchEmpty.value = false;
    tableData.value = [...originalTableData.value];
    isDataEmpty.value = tableData.value.length === 0;
    return;
  }

  // 对于启停列，需要特殊处理，因为实际数据字段是target_status
  const fieldName = field === 'enable_status' ? 'target_status' : field;

  // 前端过滤：从原始数据中筛选出符合条件的数据
  tableData.value = originalTableData.value.filter(item => values.includes(item[fieldName]));
  isSearchEmpty.value = tableData.value.length === 0;
};

const handleClearFilter = () => {
  isSearchEmpty.value = false;
  statusFilters.value = statusFilters.value.map(item => ({ ...item, checked: false }));
  enableFilters.value = enableFilters.value.map(item => ({ ...item, checked: false }));
};

const updateStatusFilters = ref([
  { label: t('同步成功'), value: 'success' },
  { label: t('同步失败'), value: 'failed' },
  { label: t('同步中'), value: 'running' },
]);
const detailsConfig = reactive({
  isShow: false,
  title: '',
  data: {},
  type: '',
});

const dataRecordFilter = ({ values }: { values: string[] }) => {
  if (values.length === 0) {
    pagination.current = 1;
  }
  dialogConfig.status = values.join(',');
  pagination.current = 1;
  fetchUpdateRecord();
};

const handleClearRecordFilter = () => {
  dialogConfig.isDataSearch = false;
  updateStatusFilters.value = updateStatusFilters.value.map(item => ({ ...item, checked: false }));
  dialogConfig.status = '';
  pagination.current = 1;
  fetchUpdateRecord();
};

//  状态为unconfirmed的行添加class
const tableRowClassName = (item) => {
  if (item.target_status === 'unconfirmed') {
    return 'unconfirmed';
  }
  return '';
};

const fetchFromStrategies = async () => {
  try {
    isLoading.value = true;
    isDataEmpty.value = false;
    isDataError.value = false;
    const res = await getFromStrategies();
    const sortedData = res.data?.sort(a => (a.target_status === 'unconfirmed' ? -1 : 1));

    // 保存原始数据副本
    originalTableData.value = sortedData || [];
    tableData.value = [...originalTableData.value];

    isDataEmpty.value = tableData.value.length === 0;
  } catch (error) {
    isDataError.value = true;
  } finally {
    isLoading.value = false;
  }
};

watchEffect(() => {
  if (props.active === 'other') {
    fetchFromStrategies();
  }
});

const dialogConfig = reactive({
  isShow: false,
  list: [],
  isDataEmpty: false,
  isDataError: false,
  isDataSearch: false,
  loading: false,
  status: '',
});

const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
});

// 数据更新记录
const showUpdateRecord = () => {
  dialogConfig.isShow = true;
  fetchUpdateRecord();
};

const fetchUpdateRecord = async () => {
  try {
    dialogConfig.loading = true;
    dialogConfig.isDataEmpty = false;
    dialogConfig.isDataError = false;

    const res = await getCollaborationSyncRecords({
      page: pagination.current,
      page_size: pagination.limit,
      statuses: dialogConfig.status,
    });
    const { count, results } = res.data;

    pagination.count = count;
    if (dialogConfig.status) {
      dialogConfig.isDataSearch = count === 0;
    } else {
      dialogConfig.isDataEmpty = count === 0;
    }
    dialogConfig.list = results;

    dialogConfig.list?.forEach((item) => {
      const { department, user } = item.summary;
      item.content = {
        create: { department: department.create, user: user.create },
        delete: { department: department.delete, user: user.delete },
        update: { department: department.update, user: user.update },
      };
    });
  } catch (error) {
    dialogConfig.isDataError = true;
  } finally {
    dialogConfig.loading = false;
  }
};

const pageLimitChange = (limit: number) => {
  pagination.limit = limit;
  pagination.current = 1;
  fetchUpdateRecord();
};

const pageCurrentChange = (current: number) => {
  pagination.current = current;
  fetchUpdateRecord();
};

const handleDetails = (item, type) => {
  detailsConfig.isShow = true;
  detailsConfig.type = type;
  detailsConfig.title = type === 'view' ? t('协同数据详情') : t('确认协同数据');
  detailsConfig.data = item;
};

const handleChange = (row) => {
  putFromStrategiesStatus(row.id).then((res) => {
    row.target_status = res?.data?.target_status;
  });
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

const updateList = () => {
  window.changeInput = false;
  fetchFromStrategies();
};
const logsDetails = ref({});
const logConfig = ref({
  isShow: false,
});

const handleLogDetails = async (row) => {
  logConfig.value.isShow = true;
  const res = await getCollaborationSyncRecordsLogs(row.id);
  logsDetails.value = res.data;
};
const beforeClose = () => {
  logConfig.value.isShow = false;
};

const handleRowExpand = async ({ row }) => {
  if (!row.createdObjs) {
    const res = await getCollaborationSyncRecordsLogs(row.id);
    Object.assign(row, {
      createdObjs: res.data?.created_objs,
      deletedObjs: res.data?.deleted_objs,
    });
  }
};

const expandConfig = reactive({
  showIcon: true,
  iconOpen: 'bk-sq-icon icon-down-shape !text-[#C4C6CC] hover:!text-[#63656E]',
  iconClose: 'bk-sq-icon icon-right-shape !text-[#C4C6CC] hover:!text-[#63656E]',
  toggleMethod: handleRowExpand,
});
</script>

<style lang="less" scoped>
.has-alert {
  height: calc(100vh - 180px) !important;
}

.user-info-wrapper {
  width: 100%;
  height: calc(100vh - 140px);
  padding: 24px;

  header {
    margin-bottom: 16px;

    .bk-button {
      margin-left: 20px;
      font-size: 14px;

      .icon-lishijilu {
        margin-right: 8px;
      }
    }
  }

  :deep(.user-info-table) {
    .unconfirmed td {
      background-color: #F2FCF5;
    }

    .type-icon {
      margin-right: 8px;
      font-size: 14px;
      color: #979BA5;
    }

    .account-status-icon {
      display: inline-block;
      width: 16px;
      height: 16px;
      margin-right: 5px;
      vertical-align: middle;
    }

    .data-source-type {
      display: flex;
      align-items: center;

      img {
        width: 14px;
        height: 14px;
      }

      span {
        margin-left: 8px;
      }
    }
  }
}

.dropdown-menu-ul {
  width: 380px;

  .dropdown-title {
    padding: 12px 16px;
    color: #63656e;
  }

  .bk-dropdown-item {
    display: flex;
    height: 100%;
    padding: 10px 16px;
    line-height: 32px;
    align-items: center;

    img {
      width: 24px;
      height: 24px;
    }

    .user-icon {
      font-size: 24px;
      color: #979ba5;
    }

    .dropdown-item {
      margin-left: 15px;

      span {
        display: block;
      }

      .dropdown-item-title {
        font-size: 14px;
        font-weight: 700;
      }

      .dropdown-item-subtitle {
        width: 300px;
        line-height: 20px;
        color: #979ba5;
        white-space: break-spaces;
      }
    }
  }
}

.update-record-dialog {
  .bk-tag {
    i {
      font-size: 14px;
      color: #C4C6CC;
    }

    .icon-file-close {
      margin-left: 12px;
    }

    span {
      color: #63656E;
    }
  }

  .update-record-table {
    padding : 28px 30px;
    .expand-wrapper {
      max-height: 300px;
      overflow-y: auto;

      &::-webkit-scrollbar {
        width: 4px;
        background-color: transparent;
      }

      &::-webkit-scrollbar-thumb {
        background-color: #dcdee5;
        border-radius: 4px;
      }
    }

    .row_expend {
      .expand-item:first-child {
        border-top: none;
      }
    }

    .row_expend:last-child {
      .expand-item:first-child {
        border-top: 1px solid #DCDEE5;
      }
    }

    .expand-item {
      display: flex;
      padding: 16px 24px;
      background: #F5F7FA;
      border-top: 1px solid #DCDEE5;

      .expand-item-content {
        width: 100%;
        box-sizing: border-box;

        i {
          margin: 0 16px 0 8px;
          font-size: 16px;
          color: #C4C6CC;
        }

        span {
          padding: 0 24px 8px 0;
        }

        .content-users, .content-departments {
          display: flex;
          align-items: baseline;
        }

        .flex {
          display: flex;
          flex-wrap: wrap;
        }
      }
    }

    .account-status-icon {
      display: inline-block;
      width: 16px;
      height: 16px;
      margin-right: 5px;
      vertical-align: middle;
    }
  }
}

.log-wrapper {
  .logs-header {
    span, .bk-tag {
      margin-right: 8px;
    }

    .logs-time, .logs-duration {
      font-size: 12px;
    }
  }

  ::v-deep .bk-modal-content {
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
      background-color: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background-color: #dcdee5;
      border-radius: 4px;
    }
  }
}
</style>
