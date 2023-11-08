<template>
  <div class="user-info-wrapper user-scroll-y">
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
        <bk-table-column label="操作">
          <template #default="{ row }">
            <span v-bk-tooltips="{
              content: '本地数据源不支持同步，请到详情页使用导入功能',
              distance: 20,
              disabled: row.plugin_id !== 'local',
            }">
              <bk-button
                text
                theme="primary"
                style="margin-right: 8px;"
                :disabled="row.plugin_id === 'local'"
                @click="handleSync(row)"
              >
                一键同步
              </bk-button>
            </span>
          </template>
        </bk-table-column>
      </bk-table>
    </bk-loading>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, Message } from 'bkui-vue';
import { onMounted, reactive, ref } from 'vue';

import Empty from '@/components/Empty.vue';
import { useTableMaxHeight } from '@/hooks/useTableMaxHeight';
import { getDataSourceList, getDataSourcePlugins, postOperationsSync } from '@/http/dataSourceFiles';
import router from '@/router/index';
import { useMainViewStore } from '@/store/mainView';
import { dataSourceStatus } from '@/utils';

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

const handleUpdateRecord = async () => {
  router.push({ name: 'syncRecords' });
};

const handleSync = async (row) => {
  const res = await postOperationsSync(row.id);
  router.push({ name: 'syncRecords' });
  const status = res.data?.status === 'failed' ? 'error' : 'success';
  Message({ theme: status, message: res.data.summary });
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
</style>
