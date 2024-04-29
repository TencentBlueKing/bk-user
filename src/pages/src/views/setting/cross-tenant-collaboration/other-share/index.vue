<template>
  <div v-bkloading="{ loading: isLoading, zIndex: 9 }" class="user-info-wrapper user-scroll-y">
    <!-- 一期不做 -->
    <!-- <header>
      <bk-button text theme="primary" @click="handleUpdateRecord">
        <i class="user-icon icon-lishijilu" />
        {{ $t('数据更新记录') }}
      </bk-button>
    </header> -->
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
          :is-data-error="isDataError"
          @handle-update="fetchCollaborationData"
        />
      </template>
      <bk-table-column prop="name" :label="$t('源租户')">
        <template #default="{ row }">
          <span>
            {{ row.name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column prop="status" :label="$t('状态')" :filter="{ list: statusFilters }">
        <template #default="{ row }">
          <div>
            <img :src="dataSourceStatus[row.status]?.icon" class="account-status-icon" />
            <span>{{ dataSourceStatus[row.status]?.text }}</span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column prop="updated_at" :label="$t('更新时间')"></bk-table-column>
      <bk-table-column prop="enable" :label="$t('启/停')" :filter="{ list: enableFilters }">
        <template #default="{ row }">
          <bk-switcher
            theme="primary"
            size="small"
            v-model="row.enable"
            :disabled="row.status === 'confirmed'"
          />
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('操作')">
        <template #default="{ row }">
          <bk-button
            v-if="row.status === 'confirmed'"
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
      </bk-table-column>
    </bk-table>
    <!-- 侧边栏 -->
    <bk-sideslider
      :width="960"
      quick-close
      v-model:isShow="detailsConfig.isShow"
      :title="detailsConfig.title"
    >
      <OperationDetails :details-config="detailsConfig" />
    </bk-sideslider>
    <!-- 数据更新记录 -->
    <bk-dialog
      width="960"
      class="update-record-dialog"
      dialog-type="show"
      :title="$t('数据更新记录')"
      :is-show="dialogConfig.isShow"
      @closed="dialogConfig.isShow = false">
      <bk-table
        class="update-record-table"
        :data="dialogConfig.list"
        :border="['outer']"
        show-overflow-tooltip
      >
        <template #empty>
          <Empty
            :is-data-empty="dialogConfig.isDataEmpty"
            :is-data-error="dialogConfig.isDataError"
            @handle-update="fetchDataUpdateRecord"
          />
        </template>
        <bk-table-column type="expand" width="60"></bk-table-column>
        <template #expandRow="row">
          <div class="expand-wrapper">
            <div class="expand-item">
              <span class="w-[60px] text-[#EA3636]">{{ $t('删除') }}:</span>
              <div class="expand-item-content">
                <div class="content-users">
                  <i class="bk-sq-icon icon-personal-user" />
                  <div class="flex">
                    <span v-for="(item, index) in row.delete.users" :key="index">
                      {{ item }}
                    </span>
                  </div>
                </div>
                <div class="content-departments">
                  <i class="bk-sq-icon icon-file-close" />
                  <div class="flex">
                    <span v-for="(item, index) in row.delete.departments" :key="index">
                      {{ item }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div class="expand-item">
              <p class="w-[60px] text-[#FF9C01]">{{ $t('变更') }}:</p>
              <div class="expand-item-content">
                <div class="content-users">
                  <i class="bk-sq-icon icon-personal-user" />
                  <div class="flex">
                    <span v-for="(item, index) in row.change.users" :key="index">
                      {{ item }}
                    </span>
                  </div>
                </div>
                <div class="content-departments">
                  <i class="bk-sq-icon icon-file-close" />
                  <div class="flex">
                    <span v-for="(item, index) in row.change.departments" :key="index">
                      {{ item }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div class="expand-item">
              <span class="w-[60px] text-[#2DCB56]">{{ $t('新增') }}:</span>
              <div class="expand-item-content">
                <div class="content-users">
                  <i class="bk-sq-icon icon-personal-user" />
                  <div class="flex">
                    <span v-for="(item, index) in row.add.users" :key="index">
                      {{ item }}
                    </span>
                  </div>
                </div>
                <div class="content-departments">
                  <i class="bk-sq-icon icon-file-close" />
                  <div class="flex">
                    <span v-for="(item, index) in row.add.departments" :key="index">
                      {{ item }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
        <bk-table-column prop="updated_at" :label="$t('时间')" width="160">
          <template #default="{ row }">
            <span>{{ row.updated_at }}</span>
          </template>
        </bk-table-column>
        <bk-table-column prop="source_tenant" :label="$t('源租户')"></bk-table-column>
        <bk-table-column :label="$t('更新内容')" width="480">
          <template #default="{ row }">
            <bk-tag theme="danger">
              {{ $t('删除') }}：
              <i class="bk-sq-icon icon-personal-user" />
              <span>{{ row.delete?.users?.length }}</span>
              <i class="bk-sq-icon icon-file-close" />
              <span>{{ row.delete?.departments?.length }}</span>
            </bk-tag>
            <bk-tag theme="warning">
              {{ $t('变更') }}：
              <i class="bk-sq-icon icon-personal-user" />
              <span>{{ row.change?.users?.length }}</span>
              <i class="bk-sq-icon icon-file-close" />
              <span>{{ row.change?.departments?.length }}</span>
            </bk-tag>
            <bk-tag theme="success">
              {{ $t('新增') }}：
              <i class="bk-sq-icon icon-personal-user" />
              <span>{{ row.add?.users?.length }}</span>
              <i class="bk-sq-icon icon-file-close" />
              <span>{{ row.add?.departments?.length }}</span>
            </bk-tag>
          </template>
        </bk-table-column>
      </bk-table>
    </bk-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';

import OperationDetails from './OperationDetails.vue';

import Empty from '@/components/Empty.vue';
import { useTableMaxHeight } from '@/hooks';
import { t } from '@/language/index';
import { useMainViewStore } from '@/store';
import { dataSourceStatus } from '@/utils';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const tableMaxHeight = useTableMaxHeight(238);
const isLoading = ref(false);
const tableData = ref([]);
const isDataEmpty = ref(false);
const isDataError = ref(false);

const statusFilters = [
  { text: t('正常'), value: 'enabled' },
  { text: t('未启用'), value: 'disabled' },
  { text: t('待确认'), value: 'confirmed' },
];

const enableFilters = [
  { text: t('启用'), value: true },
  { text: t('停用'), value: false },
];

const detailsConfig = reactive({
  isShow: false,
  title: '',
  data: {},
  type: '',
});

onMounted(() => {
  fetchCollaborationData();
});

const fetchCollaborationData = async () => {
  try {
    isLoading.value = true;
    isDataEmpty.value = false;
    isDataError.value = false;
    setTimeout(() => {
      tableData.value = [];
      if (tableData.value.length === 0) {
        isDataEmpty.value = true;
      }
    }, 1000);
  } catch (error) {
    isDataError.value = true;
  } finally {
    isLoading.value = false;
  }
};

const handleFilter = ({ checked }) => {
  if (checked.length === 0) return isDataEmpty.value = false;
  isDataEmpty.value = !tableData.value.some(item => checked.includes(item.status));
};

const dialogConfig = reactive({
  isShow: false,
  list: [],
  isDataEmpty: false,
  isDataError: false,
});

// 一期不做
// const handleUpdateRecord = async () => {
//   try {
//     dialogConfig.isShow = true;
//     dialogConfig.isDataEmpty = false;
//     dialogConfig.isDataError = false;
//     setTimeout(() => {
//       dialogConfig.list = [];
//     }, 1000);
//   } catch (error) {
//     dialogConfig.isDataError = true;
//   } finally {
//     dialogConfig.isShow = false;
//   }
// };

const handleDetails = (item, type) => {
  detailsConfig.isShow = true;
  detailsConfig.type = type;
  detailsConfig.title = type === 'view' ? t('协同数据详情') : t('确认协同数据');
  detailsConfig.data = item;
};
</script>

<style lang="less" scoped>
.user-info-wrapper {
  width: 100%;
  height: calc(100vh - 140px);
  padding: 24px;

  header {
    float: right;
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
  }
}
</style>
