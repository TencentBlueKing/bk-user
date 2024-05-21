<template>
  <div v-bkloading="{ loading: dataRecordConfig.loading, zIndex: 9 }" class="sync-records-wrapper">
    <div class="data-record-content">
      <bk-table
        class="user-info-table"
        :data="dataRecordConfig.list"
        show-overflow-tooltip
        remote-pagination
        :pagination="pagination"
        @column-filter="dataRecordFilter"
        @page-limit-change="pageLimitChange"
        @page-value-change="pageCurrentChange"
      >
        <template #empty>
          <Empty
            :is-data-empty="dataRecordConfig.isDataEmpty"
            :is-data-error="dataRecordConfig.isDataError"
            @handle-update="getSyncRecordsList"
          />
        </template>
        <bk-table-column prop="start_at" :label="$t('开始时间')" :width="160" />
        <bk-table-column prop="duration" :label="$t('耗时')">
          <template #default="{ row }">
            <span>{{ durationText(row.duration) }}</span>
          </template>
        </bk-table-column>
        <bk-table-column prop="operator" :label="$t('操作人')">
          <template #default="{ row }">
            <span>{{ row.operator || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column prop="trigger" :label="$t('触发类型')">
          <template #default="{ row }">
            <span>{{ triggeMode[row.trigger] }}</span>
          </template>
        </bk-table-column>
        <bk-table-column prop="status" :label="$t('状态')" :filter="{ list: updateStatusFilters, height: '130px' }">
          <template #default="{ row }">
            <img :src="dataRecordStatus[row.status]?.icon" class="account-status-icon" />
            <span>{{ dataRecordStatus[row.status]?.text }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')">
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
        </bk-table-column>
      </bk-table>
    </div>
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
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { ExclamationCircleShape } from 'bkui-vue/lib/icon';
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import Empty from '@/components/Empty.vue';
import SQLFile from '@/components/sql-file/SQLFile.vue';
import { getSyncLogs, getSyncRecords } from '@/http';
import { t } from '@/language/index';
import { dataRecordStatus } from '@/utils';

const route = useRoute();

const props = defineProps({
  dataSource: {
    type: Object,
    default: () => ({}),
  },
});

const dataRecordConfig = reactive({
  loading: false,
  list: [],
  // 表格请求出错
  isDataError: false,
  // 表格请求结果为空
  isDataEmpty: false,
  status: '',
});

const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
});

const logConfig = ref({
  isShow: false,
});

const logsDetails = ref({});

const triggeMode = {
  crontab: t('定时'),
  manual: t('手动'),
};

const updateStatusFilters = [
  { text: t('待执行'), value: 'pending' },
  { text: t('同步中'), value: 'running' },
  { text: t('成功'), value: 'success' },
  { text: t('失败'), value: 'failed' },
];

onMounted(() => {
  getSyncRecordsList();
});

const getSyncRecordsList = async () => {
  try {
    dataRecordConfig.loading = true;
    dataRecordConfig.isDataEmpty = false;
    dataRecordConfig.isDataError = false;
    const params = {
      page: pagination.current,
      pageSize: pagination.limit,
      status: dataRecordConfig.status,
      id: props.dataSource?.id,
    };
    const res = await getSyncRecords(params);
    dataRecordConfig.list = res.data.results;
    dataRecordConfig.isDataEmpty = res.data.count === 0;
    pagination.count = res.data.count;
    const record = dataRecordConfig.list[0];
    if (route.params.type && (record.status === 'failed' || (record.status === 'success' && record.has_warning))) {
      handleLogDetails(record);
    }
  } catch (e) {
    dataRecordConfig.isDataError = true;
    console.warn(e);
  } finally {
    dataRecordConfig.loading = false;
  }
};

const durationText = (value) => {
  if (value) {
    value = value.slice(6);
    if (value < 60) {
      return `<1 ${t('分钟')}`;
    }
    if (60 <= value && value < 3600) {
      const time = value / 60;
      const min = time.toString().split('.')[0];
      const sec = parseInt(time.toString().split('.')[1][0], 10) * 6;
      return `${min} ${t('分钟')} ${sec} ${t('秒')}`;
    }
    if (3600 <= value) {
      const time = value / 3600;
      const hour = time.toString().split('.')[0];
      const min = parseInt(time.toString().split('.')[1][0], 10) * 6;
      return `${hour}小时${min}分钟`;
    }
    return value;
  }
};

const dataRecordFilter = ({ checked }) => {
  if (checked.length === 0) {
    pagination.current = 1;
  }
  dataRecordConfig.status = checked.join(',');
  pagination.current = 1;
  getSyncRecordsList();
};

const pageLimitChange = (limit) => {
  pagination.limit = limit;
  pagination.current = 1;
  getSyncRecordsList();
};
const pageCurrentChange = (current) => {
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

const interval = setInterval(() => {
  dataRecordConfig.isDataEmpty = false;
  dataRecordConfig.isDataError = false;
  const params = {
    page: pagination.current,
    pageSize: pagination.limit,
    status: dataRecordConfig.status,
    id: props.dataSource?.id,
  };
  getSyncRecords(params).then((res) => {
    dataRecordConfig.list = res.data.results;
    dataRecordConfig.isDataEmpty = res.data.count === 0;
    pagination.count = res.data.count;
  })
    .catch(() => {
      dataRecordConfig.isDataError = true;
    });
}, 5000);

onBeforeUnmount(() => {
  clearInterval(interval);
});
</script>

<style lang="less" scoped>
.sync-records-wrapper {
  width: 100%;
  height: calc(100vh - 52px);
  padding: 28px 30px;

  :deep(.user-info-table) {
    .bk-table-head {
      table thead th {
        text-align: center;
      }

      .table-head-settings {
        border-right: none;
      }
    }

    .bk-table-footer {
      padding: 0 15px;
      background: #fff;
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
