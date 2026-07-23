<template>
  <div v-bkloading="{ loading: dataRecordConfig.loading, zIndex: 10 }" class="sync-records-wrapper">
    <div class="data-record-content">
      <Table
        class="user-info-table"
        :data="dataRecordConfig.list"
        :pagination="pagination"
        :border="'inner'"
        :settings="settings"
        :show-settings="true"
        @filter-change="handleFilterChange"
        @page-limit-change="pageLimitChange"
        @page-value-change="pageCurrentChange"
        @setting-change="handleSettingChange"
      >
        <template #empty>
          <Empty
            :type="curExceptionType"
            @clear="handleClearSearch"
            @refresh="getSyncRecordsList"
          />
        </template>
        <TableColumn
          field="start_at"
          :label="$t('开始时间')"
          show-overflow="tooltip"
          :min-width="160"
        />
        <TableColumn
          field="duration"
          :label="$t('耗时')"
          show-overflow="tooltip"
          :min-width="120"
        >
          <template #default="{ row }">
            <span>{{ durationText(row.duration) }}</span>
          </template>
        </TableColumn>
        <TableColumn
          field="plugin"
          :label="$t('数据源类型')"
          show-overflow="tooltip"
          :min-width="160"
        >
          <template #default="{ row }">
            <span>{{ row?.plugin?.name || '--' }}</span>
          </template>
        </TableColumn>
        <TableColumn
          field="operator"
          :label="$t('操作人')"
          show-overflow="tooltip"
          :min-width="120"
        >
          <template #default="{ row }">
            <DisplayName :user-id="row.operator" />
          </template>
        </TableColumn>
        <TableColumn
          field="trigger"
          :label="$t('触发类型')"
          show-overflow="tooltip"
          :min-width="80"
        >
          <template #default="{ row }">
            <span>{{ triggeMode[row.trigger] }}</span>
          </template>
        </TableColumn>
        <TableColumn
          field="status"
          :label="$t('状态')"
          show-overflow="tooltip"
          filter-multiple
          :filters="updateStatusFilters"
          :min-width="120"
        >
          <template #default="{ row }">
            <img :src="dataRecordStatus[row.status]?.icon" class="account-status-icon" />
            <span>{{ dataRecordStatus[row.status]?.text }}</span>
          </template>
        </TableColumn>
        <TableColumn
          field="action"
          :label="$t('操作')"
          :min-width="100"
        >
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
    </div>
    <bk-sideslider
      ext-cls="log-wrapper"
      :is-show="logConfig.isShow"
      :title="$t('日志详情')"
      :width="960"
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
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { ExclamationCircleShape } from 'bkui-vue/lib/icon';
import { onBeforeUnmount, onMounted, reactive, ref, toRef } from 'vue';
import { useRoute } from 'vue-router';

import { Table, TableColumn } from '@blueking/table';

import DisplayName from './display-name.vue';

import 'tippy.js/dist/tippy.css';
import 'tippy.js/themes/light.css';
import Empty from '@/components/SearchEmpty.vue';
import SQLFile from '@/components/sql-file/SQLFile.vue';
import useTableEmpty from '@/hooks/use-table-empty';
import { getSyncLogs, getSyncRecords } from '@/http';
import { SyncRecordsParams } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';
import { dataRecordStatus, durationText } from '@/utils';

const props = defineProps({
  dataSource: {
    type: Object,
    default: () => ({}),
  },
});

const route = useRoute();

const dataRecordConfig = reactive({
  loading: false,
  list: [],
  status: '',
});

const settings = reactive({
  checked: ['start_at', 'duration', 'plugin', 'operator', 'trigger', 'status', 'action'],
  size: 'small',
});

const { setTypeToError, clearErrorType, curExceptionType } = useTableEmpty({
  filters: toRef(dataRecordConfig, 'status'),
  clearTableData: () => {
    dataRecordConfig.list = [];
  }
});

const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
  remote: true,
});

const logConfig = ref({
  isShow: false,
});

const logsDetails = ref({});

const triggeMode = {
  crontab: t('定时'),
  manual: t('手动'),
};

const updateStatusFilters = ref([
  { label: t('同步中'), value: 'pending,running' },
  { label: t('同步成功'), value: 'success' },
  { label: t('同步失败'), value: 'failed' },
]);

const interval = ref(null);
onMounted(() => {
  getSyncRecordsList();
  interval.value =  setInterval(() => {
    handleSyncRecords();
  }, 5000);
});

const getSyncRecordsList = async () => {
  try {
    dataRecordConfig.loading = true;
    clearErrorType();
    const { list } = await handleSyncRecords();
    const record = list[0];
    if (route.params.type && (record.status === 'failed' || (record.status === 'success' && record.has_warning))) {
      handleLogDetails(record);
    }
  } catch (e) {
    console.warn(e);
    setTypeToError();
  } finally {
    dataRecordConfig.loading = false;
  }
};

const handleClearSearch = () => {
  dataRecordConfig.status = '';
  updateStatusFilters.value = updateStatusFilters.value.map(item => ({ ...item, checked: false }));
  pagination.current = 1;
  getSyncRecordsList();
};

// 增加防抖，避免 bk-table 筛选重置时触发两次，导致重复请求
const handleFilterChange = ({ values }: { values: string[] }) => {
  if (values.length === 0) {
    pagination.current = 1;
  }
  dataRecordConfig.status = values.join(',');
  pagination.current = 1;
  getSyncRecordsList();
};

const pageLimitChange = (limit: number) => {
  pagination.limit = limit;
  pagination.current = 1;
  getSyncRecordsList();
};
const pageCurrentChange = (current: number) => {
  pagination.current = current;
  getSyncRecordsList();
};

const handleLogDetails = async (row) => {
  logConfig.value.isShow = true;
  const res = await getSyncLogs(row.id);
  logsDetails.value = res.data;
};

const beforeClose = () => {
  logConfig.value.isShow = false;
};

const handleSettingChange = (data: any) => {
  settings.size = data.size as string;
};

const handleSyncRecords = async () => {
  const params: SyncRecordsParams = {
    page: pagination.current,
    page_size: pagination.limit,
    statuses: dataRecordConfig.status,
  };
  try {
    const res = await getSyncRecords(props.dataSource?.id, params);
    dataRecordConfig.list = res.data.results;
    pagination.count = res.data.count;
    // stop time polling
    const curStatus = res.data.results?.[0]?.status;
    if (curStatus === 'success' || curStatus === 'failed') {
      clearInterval(interval.value);
    }

    return {
      list: res.data.results,
    };
  } catch (e) {
    console.warn(e);
  }
};

onBeforeUnmount(() => {
  clearInterval(interval.value);
});
</script>

<style lang="less" scoped>
.sync-records-wrapper {
  width: 100%;
  height: calc(100vh - 52px);
  padding: 28px 15px 28px 30px;

  :deep(.user-info-table) {
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

    .circle-shape {
      font-size: 14px;
      color: #FF9C01;
      vertical-align: middle;
      cursor: pointer;
    }
  }

  .back-previous {
    display: inline-block;
    margin-bottom: 16px;
    font-size: 14px;
    font-weight: 700;
    color: #63656E;
    cursor: pointer;

    .icon-arrow-left {
      margin-right: 8px;
      font-size: 18px;
      color: #3a84ff;
    }
  }

  .data-record-content {
    background: #fff;

    .title {
      padding: 16px 0;
      font-size: 16px;
      font-weight: 700;
      line-height: 24px;
      color: #313238;
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

  // ::v-deep .bk-modal-content {
  //   overflow-y: auto;

  //   &::-webkit-scrollbar {
  //     width: 4px;
  //     background-color: transparent;
  //   }

  //   &::-webkit-scrollbar-thumb {
  //     background-color: #dcdee5;
  //     border-radius: 4px;
  //   }
  // }
}
</style>

<style lang="less">
/* 隐藏 setting Tab 的滚动条 */
.action-tab-wrapper {
  overflow-y: auto !important;
}
</style>

