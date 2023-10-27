<template>
  <div class="user-info-wrapper user-scroll-y">
    <template v-if="!showDataUpdateRecord">
      <header>
        <bk-dropdown placement="bottom-start">
          <bk-button theme="primary">
            <i class="user-icon icon-add-2 mr8" />
            新建数据源
          </bk-button>
          <template #content>
            <bk-dropdown-menu ext-cls="dropdown-menu-ul">
              <p class="dropdown-title" v-if="state.typeList.length > 0">数据源类型选择</p>
              <p class="dropdown-title" v-else>暂无数据源类型</p>
              <bk-dropdown-item
                v-for="item in state.typeList"
                :key="item"
                @click="newDataSource(item)"
              >
                <img v-if="item.logo" :src="item.logo">
                <div class="dropdown-item">
                  <span class="dropdown-item-title">{{ item.name }}</span>
                  <span class="dropdown-item-subtitle">{{ item.description }}</span>
                </div>
              </bk-dropdown-item>
            </bk-dropdown-menu>
          </template>
        </bk-dropdown>
        <div class="header-right">
          <bk-input
            v-model="searchVal"
            placeholder="搜索数据源名称"
            type="search"
            clearable
            @enter="handleEnter"
            @clear="handleClear"
          />
          <bk-button text theme="primary" @click="handleUpdateRecord">
            <i class="user-icon icon-lishijilu" />
            数据更新记录
          </bk-button>
        </div>
      </header>
      <bk-loading :loading="state.isLoading">
        <bk-table
          class="user-info-table"
          :data="state.list"
          :border="['outer']"
          :max-height="tableMaxHeight"
          show-overflow-tooltip
          @column-filter="handleFilter"
        >
          <template #empty>
            <Empty
              :is-data-empty="state.isDataEmpty"
              :is-search-empty="state.isEmptySearch"
              :is-data-error="state.isDataError"
              @handleEmpty="handleClear"
              @handleUpdate="handleUpdateRecord"
            />
          </template>
          <bk-table-column prop="name" label="数据源名称">
            <template #default="{ row }">
              <bk-button text theme="primary" @click="handleClick(row)">
                {{ row.name }}
              </bk-button>
            </template>
          </bk-table-column>
          <bk-table-column prop="plugin_id" label="数据源类型">
            <template #default="{ row }">
              <div class="data-source-type" v-for="item in state.typeList" :key="item">
                <img v-if="item.id === row.plugin_id && item.logo" :src="item.logo">
                <span v-if="item.id === row.plugin_id">{{ row.plugin_name }}</span>
              </div>
            </template>
          </bk-table-column>
          <bk-table-column prop="status" label="状态" :filter="{ list: statusFilters }">
            <template #default="{ row }">
              <div>
                <img :src="dataSourceStatus[row.status]?.icon" class="account-status-icon" />
                <span>{{ dataSourceStatus[row.status]?.text }}</span>
              </div>
            </template>
          </bk-table-column>
          <bk-table-column prop="updater" label="更新人">
            <template #default="{ row }">
              <span>{{ row.updater || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column prop="updated_at" label="更新时间"></bk-table-column>
        </bk-table>
      </bk-loading>
    </template>
    <template v-else>
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
          :pagination="openPaging ? pagination : openPaging"
          @column-filter="dataRecordFilter"
          @page-limit-change="pageLimitChange"
          @page-value-change="pageCurrentChange"
        >
          <template #empty>
            <Empty
              :is-data-empty="dataRecordConfig.isDataEmpty"
              :is-data-error="dataRecordConfig.isDataError"
              @handleUpdate="updateDataRecord"
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
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';

import Empty from '@/components/Empty.vue';
import SQLFile from '@/components/sql-file/SQLFile.vue';
import { useTableMaxHeight } from '@/hooks/useTableMaxHeight';
import { getDataSourceList, getDataSourcePlugins, getSyncLogs, getSyncRecords } from '@/http/dataSourceFiles';
import router from '@/router/index';
import { useMainViewStore } from '@/store/mainView';
import { dataRecordStatus, dataSourceStatus } from '@/utils';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const tableMaxHeight = useTableMaxHeight(238);
const searchVal = ref('');
const state = reactive({
  isLoading: false,
  list: [],
  // 搜索结果为空
  isEmptySearch: false,
  // 表格请求出错
  isDataError: false,
  // 表格请求结果为空
  isDataEmpty: false,
  typeList: [],
});

const statusFilters = [
  { text: '正常', value: 'enabled' },
  { text: '未启用', value: 'disabled' },
];

onMounted(() => {
  fetchDataSourceList();
  getDataSourcePlugins().then((res) => {
    state.typeList = res.data;
  });
});

const fetchDataSourceList = async () => {
  try {
    state.isLoading = true;
    state.isDataEmpty = false;
    state.isEmptySearch = false;
    state.isDataError = false;
    const res = await getDataSourceList(searchVal.value);
    if (res.data.length === 0) {
      searchVal.value === '' ? state.isDataEmpty = true : state.isEmptySearch = true;
    }
    state.list = res.data;
    state.isLoading = false;
  } catch (error) {
    state.isDataError = true;
  } finally {
    state.isLoading = false;
  }
};

// 搜索数据源列表
const handleEnter = (value: string) => {
  searchVal.value = value;
  fetchDataSourceList();
};

const handleClear = () => {
  searchVal.value = '';
  fetchDataSourceList();
};

const handleFilter = ({ checked }) => {
  if (checked.length === 0) return state.isDataEmpty = false;
  state.isDataEmpty = !state.list.some(item => checked.includes(item.status));
};

function handleClick(item) {
  router.push({
    name: 'dataConfDetails',
    params: {
      id: item.id,
      status: item.status,
    },
  });
}
function newDataSource(item) {
  router.push({
    name: 'newLocal',
    params: {
      type: item.id,
    },
  });
}

const showDataUpdateRecord = ref(false);

const dataRecordConfig = reactive({
  loading: false,
  list: [],
  // 表格请求出错
  isDataError: false,
  // 表格请求结果为空
  isDataEmpty: false,
});

const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
});

const updateStatusFilters = [
  { text: '待执行', value: 'pending' },
  { text: '同步中', value: 'running' },
  { text: '成功', value: 'success' },
  { text: '失败', value: 'failed' },
];

const openPaging = ref(true);
const dataRecordFilter = ({ checked }) => {
  dataRecordConfig.isDataEmpty = checked.length === 0
    ? false
    : !dataRecordConfig.list.some(item => checked.includes(item.status));
  openPaging.value = !dataRecordConfig.isDataEmpty;
};

const pageLimitChange = (limit) => {
  pagination.limit = limit;
  pagination.current = 1;
  handleUpdateRecord();
};
const pageCurrentChange = (current) => {
  pagination.current = current;
  handleUpdateRecord();
};

const handleUpdateRecord = async () => {
  try {
    showDataUpdateRecord.value = true;
    dataRecordConfig.loading = true;
    dataRecordConfig.isDataEmpty = false;
    dataRecordConfig.isDataError = false;
    const params = {
      page: pagination.current,
      pageSize: pagination.limit,
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

const triggeMode = {
  crontab: '定时触发',
  manual: '手动触发',
};

const handleBack = () => {
  showDataUpdateRecord.value = false;
  pagination.current = 1;
  pagination.limit = 10;
  fetchDataSourceList();
};

const logConfig = ref({
  isShow: false,
});

const logsDetails = ref({});

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
.user-info-wrapper {
  width: 100%;
  height: calc(100vh - 140px);
  padding: 16px 24px;

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .header-right {
      display: flex;
      align-items: center;

      .bk-input {
        width: 400px;
      }

      .bk-button {
        margin-left: 20px;
        font-size: 14px;

        .icon-lishijilu {
          margin-right: 8px;
        }
      }
    }
  }

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

.dropdown-menu-ul {
  width: 380px;
  font-family: MicrosoftYaHei;

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
