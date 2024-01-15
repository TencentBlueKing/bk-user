<template>
  <div class="auth-source-wrapper user-scroll-y">
    <header>
      <bk-button theme="primary" @click="newAuthSource">
        <i class="user-icon icon-add-2 mr8" />
        {{ $t('新建') }}
      </bk-button>
      <bk-input
        class="header-right"
        v-model="searchVal"
        :placeholder="$t('搜索认证源名称')"
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
        :max-height="tableMaxHeight"
        show-overflow-tooltip
        @column-filter="handleFilter"
      >
        <template #empty>
          <Empty
            :is-data-empty="isDataEmpty"
            :is-search-empty="isEmptySearch"
            :is-data-error="isDataError"
            @handleEmpty="handleClear"
            @handleUpdate="fetchAuthSourceList"
          />
        </template>
        <bk-table-column prop="name" :label="$t('认证源名称')">
          <template #default="{ row }">
            <bk-button text theme="primary" @click="handleClick(row)">
              {{ row.name }}
            </bk-button>
          </template>
        </bk-table-column>
        <bk-table-column prop="plugin.id" :label="$t('类型')">
          <template #default="{ row }">
            <div class="data-source-type">
              <img :src="row.plugin?.logo">
              <span>{{ row.plugin?.name }}</span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column prop="matched_data_sources" :label="$t('匹配数据源')">
          <template #default="{ row }">
            <bk-tag v-for="(item, index) in row.matched_data_sources" :key="index">{{ item }}</bk-tag>
          </template>
        </bk-table-column>
        <bk-table-column prop="status" :label="$t('状态')" :filter="{ list: statusFilters }">
          <template #default="{ row }">
            <div>
              <img :src="dataSourceStatus[row.status]?.icon" class="status-icon" />
              <span>{{ dataSourceStatus[row.status]?.text }}</span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column prop="updater" :label="$t('更新人')">
          <template #default="{ row }">
            <span>{{ row.updater || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column prop="updated_at" :label="$t('更新时间')"></bk-table-column>
        <bk-table-column :label="$t('操作')" width="150">
          <template #default="{ row }">
            <bk-button class="mr10" theme="primary" text @click="handleEdit(row)">{{ $t('编辑') }}</bk-button>
            <!-- <bk-popover
              class="dot-menu"
              placement="bottom-start"
              theme="light"
              :arrow="false">
              <i class="user-icon icon-more dot-menu-trigger"></i>
              <template #content>
                <ul class="dot-menu-list">
                  <li class="dot-menu-item">删除</li>
                </ul>
              </template>
            </bk-popover> -->
          </template>
        </bk-table-column>
      </bk-table>
    </bk-loading>
    <bk-sideslider
      v-model:isShow="detailsConfig.show"
      :title="detailsConfig.title"
      quick-close
      width="640"
    >
      <template #header>
        <span>{{ detailsConfig.title }}</span>
        <div>
          <bk-button
            outline
            theme="primary"
            @click="handleEdit(currentRow)">
            {{ $t('编辑') }}
          </bk-button>
          <!-- <bk-button>删除</bk-button> -->
        </div>
      </template>
      <template #default>
        <ViewDetails :data="authDetails" @updateRow="updateRow" />
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';

import ViewDetails from './ViewDetails.vue';

import Empty from '@/components/Empty.vue';
import { useTableMaxHeight } from '@/hooks/useTableMaxHeight';
import { getIdps } from '@/http/authSourceFiles';
import { t } from '@/language/index';
import router from '@/router/index';
import { dataSourceStatus } from '@/utils';

const searchVal = ref('');
const isLoading = ref(false);
const tableData = ref([]);
const isDataEmpty = ref(false);
const isEmptySearch = ref(false);
const isDataError = ref(false);
const tableMaxHeight = useTableMaxHeight(150);

const statusFilters = [
  { text: t('正常'), value: 'enabled' },
  { text: t('未启用'), value: 'disabled' },
];

onMounted(() => {
  fetchAuthSourceList();
});

const fetchAuthSourceList = async () => {
  try {
    isLoading.value = true;
    isDataEmpty.value = false;
    isEmptySearch.value = false;
    isDataError.value = false;
    const res = await getIdps(searchVal.value);
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
  fetchAuthSourceList();
};

const handleClear = () => {
  searchVal.value = '';
  fetchAuthSourceList();
};

const handleFilter = ({ checked }) => {
  if (checked.length === 0) return isDataEmpty.value = false;
  isDataEmpty.value = !tableData.value.some(item => checked.includes(item.status));
};

const newAuthSource = () => {
  router.push({
    name: 'newAuthSource',
  });
};

const detailsConfig = reactive({
  show: false,
  title: t('认证源详情'),
});

const authDetails = ref({});

const handleClick = (row) => {
  authDetails.value = row;
  detailsConfig.show = true;
};

const handleEdit = (row) => {
  router.push({
    name: 'editAuthSource',
    params: {
      type: row.plugin?.id,
      id: row.id,
    },
  });
};

const currentRow = ref({});
const updateRow = (row) => {
  currentRow.value = row;
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

    .status-icon {
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

:deep(.bk-sideslider-title) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px 0 50px !important;

  .bk-button {
    padding: 5px 17px !important;
  }
}
</style>
