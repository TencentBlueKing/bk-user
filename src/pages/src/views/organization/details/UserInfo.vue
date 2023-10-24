<template>
  <div class="user-info-wrapper user-scroll-y">
    <header>
      <bk-checkbox
        :class="{ 'is-status': isTenant }"
        v-model="isCurrentUsers"
        @change="emit('changeUsers', isCurrentUsers ? false : true)">
        仅显示本级用户（<span>{{ props.pagination.count }}</span>）
      </bk-checkbox>
      <bk-input
        class="header-right"
        v-model="searchValue"
        placeholder="搜索用户名、全名"
        type="search"
        clearable
        @enter="handleEnter"
        @clear="handleClear"
      />
    </header>
    <bk-table
      class="user-info-table"
      remote-pagination
      :data="userData"
      :pagination="props.pagination"
      :border="['outer']"
      show-overflow-tooltip
      @page-limit-change="pageLimitChange"
      @page-value-change="pageCurrentChange"
    >
      <template #empty>
        <Empty
          :is-data-empty="props.isDataEmpty"
          :is-search-empty="props.isEmptySearch"
          :is-data-error="props.isDataError"
          @handleEmpty="handleClear"
          @handleUpdate="handleClear" />
      </template>
      <bk-table-column prop="username" label="用户名">
        <template #default="{ row }">
          <bk-button text theme="primary" @click="handleClick(row)">
            {{ row.username }}
          </bk-button>
        </template>
      </bk-table-column>
      <bk-table-column prop="full_name" label="全名" />
      <!-- <bk-table-column prop="status" label="状态">
        <template #default="{ row }">
          <div>
            <img :src="statusIcon[row.status]?.icon" class="account-status-icon" />
            <span>{{ statusIcon[row.status]?.text }}</span>
          </div>
        </template>
      </bk-table-column> -->
      <bk-table-column prop="email" label="邮箱" />
      <bk-table-column prop="phone" label="手机号" />
      <bk-table-column prop="departments" label="组织">
        <template #default="{ row }">
          <span>{{ formatConvert(row.departments) }}</span>
        </template>
      </bk-table-column>
    </bk-table>
    <!-- 查看/编辑用户 -->
    <bk-sideslider
      ext-cls="details-edit-wrapper"
      :width="640"
      :is-show="detailsConfig.isShow"
      :title="detailsConfig.title"
      :before-close="handleBeforeClose"
      quick-close
    >
      <template #header>
        <span>{{ detailsConfig.title }}</span>
        <!-- <bk-button>删除</bk-button> -->
      </template>
      <ViewUser :user-data="state.userInfo" />
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, defineProps, inject, reactive, ref } from 'vue';

import ViewUser from './ViewUser.vue';

import Empty from '@/components/Empty.vue';
import {
  getTenantUsers,
} from '@/http/organizationFiles';
import { formatConvert } from '@/utils';

const editLeaveBefore = inject('editLeaveBefore');

const props = defineProps({
  userData: {
    type: Object,
    default: () => ({}),
  },
  isDataEmpty: {
    type: Boolean,
    default: false,
  },
  isEmptySearch: {
    type: Boolean,
    default: false,
  },
  isDataError: {
    type: Boolean,
    default: false,
  },
  pagination: {
    type: Object,
    default: () => ({}),
  },
  keyword: {
    type: String,
    default: '',
  },
  isTenant: {
    type: Boolean,
    default: false,
  },
});
const emit = defineEmits(['searchUsers', 'changeUsers', 'updatePageLimit', 'updatePageCurrent']);
const isCurrentUsers = ref(true);
const detailsConfig = reactive({
  isShow: false,
  title: '',
});
const searchValue = ref(props.keyword);

const state = reactive({
  userInfo: {},
});

const handleClick = async (item: any) => {
  const res = await getTenantUsers(item.id);
  state.userInfo = res.data;
  detailsConfig.title = '用户详情';
  detailsConfig.isShow = true;
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    detailsConfig.isShow = false;
  } else {
    detailsConfig.isShow = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};
// 搜索用户名、全名
const handleEnter = (value: string) => {
  emit('searchUsers', value);
};
const handleClear = () => {
  searchValue.value = '';
  emit('searchUsers', '');
};

const pageLimitChange = (limit) => {
  emit('updatePageLimit', limit);
};
const pageCurrentChange = (current) => {
  emit('updatePageCurrent', current);
};
</script>

<style lang="less" scoped>
.user-info-wrapper {
  width: 100%;
  height: calc(100vh - 140px);
  padding: 24px;

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .is-status {
      visibility: hidden;
    }

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

    .account-status-icon {
      width: 16px;
      height: 16px;
      margin-right: 5px;
      vertical-align: middle;
    }
  }
}

.details-edit-wrapper {
  :deep(.bk-sideslider-title) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px 0 50px !important;

    .bk-button {
      padding: 5px 17px !important;
    }
  }

  :deep(.bk-modal-content) {
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
      background-color: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background-color: #dcdee5;
      border-radius: 4px;
    }

    &:hover {
      &::-webkit-scrollbar-thumb {
        background-color: #979ba5;
      }
    }
  }
}
</style>
