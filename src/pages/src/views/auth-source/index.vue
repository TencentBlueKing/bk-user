<template>
  <div class="auth-source-wrapper user-scroll-y">
    <header>
      <bk-button theme="primary" @click="newAuthSource">
        <i class="user-icon icon-add-2 mr8" />
        新建认证源
      </bk-button>
      <bk-input
        class="header-right"
        v-model="searchVal"
        placeholder="搜索认证源名称"
        type="search"
        clearable
        @enter="handleEnter"
        @clear="handleClear"
      />
    </header>
    <bk-loading :loading="isLoading">
      <bk-table
        class="user-info-table"
        :data="tableData"
        :border="['outer']"
        :pagination="pagination"
        show-overflow-tooltip
        settings
      >
        <template #empty>
          <Empty
            :is-data-empty="isDataEmpty"
            :is-search-empty="isEmptySearch"
            :is-data-error="isDataError"
            @handleEmpty="handleClear"
            @handleUpdate="fetchDataSourceList"
          />
        </template>
        <bk-table-column prop="name" label="认证源名称">
          <template #default="{ row }">
            <bk-button text theme="primary" @click="handleClick(row)">
              {{ row.name }}
            </bk-button>
          </template>
        </bk-table-column>
        <bk-table-column prop="plugin_id" label="类型">
          <template #default="{ row }">
            <div class="data-source-type" v-for="item in typeList" :key="item">
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
        <bk-table-column label="操作" width="150">
          <template #default="{ row }">
            <bk-button class="mr10" theme="primary" text @click="handleEdit(row)">编辑</bk-button>
            <bk-popover
              class="dot-menu"
              placement="bottom-start"
              theme="light"
              :arrow="false">
              <i class="user-icon icon-more dot-menu-trigger"></i>
              <template #content>
                <ul class="dot-menu-list">
                  <li class="dot-menu-item">导入</li>
                  <li class="dot-menu-item">导出</li>
                </ul>
              </template>
            </bk-popover>
          </template>
        </bk-table-column>
      </bk-table>
    </bk-loading>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';

import Empty from '@/components/Empty.vue';
import { getDataSourceList, getDataSourcePlugins } from '@/http/dataSourceFiles';
import router from '@/router/index';
import { dataSourceStatus } from '@/utils';

const searchVal = ref('');
const isLoading = ref(false);
const tableData = ref([]);
const typeList = ref([]);
const isDataEmpty = ref(false);
const isEmptySearch = ref(false);
const isDataError = ref(false);

const statusFilters = [
  { text: '正常', value: 'enabled' },
  { text: '未启用', value: 'disabled' },
];

const pagination = reactive({
  count: 0,
  current: 1,
  limit: 10,
});

onMounted(() => {
  fetchDataSourceList();
  getDataSourcePlugins().then((res) => {
    typeList.value = res.data;
  });
});

const fetchDataSourceList = async () => {
  try {
    isLoading.value = true;
    isDataEmpty.value = false;
    isEmptySearch.value = false;
    isDataError.value = false;
    const res = await getDataSourceList(searchVal.value);
    if (res.data.length === 0) {
      searchVal.value === '' ? isDataEmpty.value = true : isEmptySearch.value = true;
    }
    tableData.value = res.data;
    isLoading.value = false;
  } catch (error) {
    isDataError.value = true;
  } finally {
    isLoading.value = false;
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

const newAuthSource = () => {
  router.push({
    name: 'newAuthSource',
  });
};
</script>

<style lang="less" scoped>
.auth-source-wrapper {
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

.dot-menu {
  display: inline-block;
  vertical-align: middle;
}

.tippy-tooltip.dot-menu-theme {
  padding: 0;
}

.dot-menu-trigger {
  display: inline-block;
  width: 30px;
  height: 30px;
  font-size: 0;
  line-height: 30px;
  color: #979BA5;
  text-align: center;
  vertical-align: middle;
  cursor: pointer;
  border-radius: 50%;
}

.dot-menu-trigger:hover {
  color: #3A84FF;
  background-color: #EBECF0;
}

.dot-menu-trigger::before {
  display: inline-block;
  width: 3px;
  height: 3px;
  background-color: currentcolor;
  border-radius: 50%;
  content: "";
  box-shadow: 0 -4px 0 currentcolor, 0 4px 0 currentcolor;
}

.dot-menu-list {
  min-width: 50px;
  padding: 5px 0;
  margin: 0;
  list-style: none;
}

.dot-menu-list .dot-menu-item {
  padding: 0 10px;
  font-size: 12px;
  line-height: 26px;
  color: #63656e;
  cursor: pointer;

  &:hover {
    color: #3a84ff;
    background-color: #eaf3ff;
  }
}
</style>
