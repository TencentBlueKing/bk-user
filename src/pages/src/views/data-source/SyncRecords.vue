<template>
  <div class="sync-records-wrapper user-scroll-y">
    <span class="back-previous" @click="handleBack">
      <i class="user-icon icon-arrow-left" />
      返回上一页
    </span>
    <bk-loading class="data-record-content" :loading="dataRecordConfig.loading">
      <p class="title">数据更新记录</p>
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
            @handleUpdate="getSyncRecordsList"
          />
        </template>
        <bk-table-column prop="start_at" label="开始时间" />
        <bk-table-column prop="duration" label="耗时">
          <template #default="{ row }">
            <span>{{ durationText(row.duration) }}</span>
          </template>
        </bk-table-column>
        <bk-table-column prop="operator" label="操作人">
          <template #default="{ row }">
            <span>{{ row.operator || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column prop="trigger" label="触发类型">
          <template #default="{ row }">
            <span>{{ triggeMode[row.trigger] }}</span>
          </template>
        </bk-table-column>
        <bk-table-column prop="data_source_name" label="数据源" />
        <bk-table-column prop="status" label="状态" :filter="{ list: updateStatusFilters }">
          <template #default="{ row }">
            <img :src="dataRecordStatus[row.status]?.icon" class="account-status-icon" />
            <span>{{ dataRecordStatus[row.status]?.text }}</span>
          </template>
        </bk-table-column>
        <bk-table-column label="操作">
          <template #default="{ row }">
            <bk-button
              text
              theme="primary"
              style="margin-right: 8px;"
              @click="handleLogDetails(row)"
            >
              日志详情
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </bk-loading>
    <bk-sideslider
      ext-cls="log-wrapper"
      :is-show="logConfig.isShow"
      title="日志详情"
      :width="960"
      quick-close
      :before-close="beforeClose"
    >
      <template #header>
        <div class="logs-header">
          <span>日志详情</span>
          <bk-tag>{{ logsDetails.start_at }}</bk-tag>
          <bk-tag :theme="dataRecordStatus[logsDetails.status]?.theme">
            {{ dataRecordStatus[logsDetails.status]?.text }}
          </bk-tag>
          <span class="logs-duration">总耗时 {{ durationText(logsDetails.duration) }}</span>
        </div>
      </template>
      <template #default>
        <SQLFile
          v-model="logsDetails.logs"
          readonly
          title="执行日志" />
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';

import Empty from '@/components/Empty.vue';
import SQLFile from '@/components/sql-file/SQLFile.vue';
import { getSyncLogs, getSyncRecords } from '@/http/dataSourceFiles';
import router from '@/router/index';
import { dataRecordStatus } from '@/utils';

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
  crontab: '定时',
  manual: '手动',
};

const updateStatusFilters = [
  { text: '待执行', value: 'pending' },
  { text: '同步中', value: 'running' },
  { text: '成功', value: 'success' },
  { text: '失败', value: 'failed' },
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
    };
    const res = await getSyncRecords(params);
    dataRecordConfig.list = res.data.results;
    dataRecordConfig.isDataEmpty = res.data.count === 0;
    pagination.count = res.data.count;
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
      return '<1 分钟';
    }
    if (60 <= value && value < 3600) {
      const time = value / 60;
      const min = time.toString().split('.')[0];
      const sec = parseInt(time.toString().split('.')[1][0], 10) * 6;
      return `${min} 分钟 ${sec} 秒`;
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

const handleBack = () => {
  pagination.current = 1;
  pagination.limit = 10;
  router.push({ name: 'local' });
};

const dataRecordFilter = ({ checked }) => {
  if (checked.length === 0) {
    pagination.current = 1;
  }
  dataRecordConfig.status = checked;
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
  logsDetails.value = {};
  logConfig.value.isShow = false;
};
</script>

<style lang="less" scoped>
.sync-records-wrapper {
  width: 100%;
  height: calc(100vh - 140px);
  padding: 16px 24px;

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
    padding: 0 24px 24px;
    background: #fff;

    .title {
      padding: 16px 0;
      font-family: MicrosoftYaHei-Bold;
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
