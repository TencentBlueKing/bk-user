<template>
  <div class="user-info-wrapper user-scroll-y">
    <header>
      <div>
        <bk-checkbox
          v-if="!isTenant"
          v-model="isCurrentUsers"
          @change="emit('changeUsers', isCurrentUsers ? false : true)">
          {{ $t('仅显示本级用户') }}（<span>{{ props.pagination.count }}</span>）
        </bk-checkbox>
      </div>
      <bk-input
        class="header-right"
        v-model="searchValue"
        :placeholder="$t('搜索用户名、姓名')"
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
      :settings="tableSettings"
      @page-limit-change="pageLimitChange"
      @page-value-change="pageCurrentChange"
      @setting-change="emit('handleSettingChange', $event)">
      >
      <template #empty>
        <Empty
          :is-data-empty="props.isDataEmpty"
          :is-search-empty="props.isEmptySearch"
          :is-data-error="props.isDataError"
          @handle-empty="handleClear"
          @handle-update="handleClear" />
      </template>
      <template v-for="(item, index) in tableSettings.fields" :key="index">
        <bk-table-column :prop="item.field" :label="item.name">
          <template #default="{ row }">
            <bk-button v-if="item.field === 'username'" text theme="primary" @click="handleClick(row)">
              {{ row.username }}
            </bk-button>
            <span v-else-if="item.field === 'departments'">
              {{ formatConvert(row.departments) }}
            </span>
            <span v-else>{{ getTableValue(row, item) }}</span>
          </template>
        </bk-table-column>
      </template>
    </bk-table>
    <!-- 查看/编辑用户 -->
    <div v-if="showSideBar">
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
  </div>
</template>

<script setup lang="ts">
import { defineEmits, defineProps, inject, reactive, ref } from 'vue';

import ViewUser from './ViewUser.vue';

import Empty from '@/components/Empty.vue';
import { useCustomFields } from '@/hooks';
import {
  getFields,
  getTenantOrganizationUsers,
} from '@/http';
import { t } from '@/language/index';
import { formatConvert, getTableValue } from '@/utils';

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
  tableSettings: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(['searchUsers', 'changeUsers', 'updatePageLimit', 'updatePageCurrent', 'handleSettingChange']);

const editLeaveBefore = inject('editLeaveBefore');

const isCurrentUsers = ref(true);
const detailsConfig = reactive({
  isShow: false,
  title: '',
});
const searchValue = ref(props.keyword);

const state = reactive({
  userInfo: {},
});

const showSideBar = ref(false);
// 销毁侧栏，防止tips不消失
const hideSideBar = () => {
  setTimeout(() => {
    showSideBar.value = false;
  }, 300);
};

const handleClick = async (item: any) => {
  showSideBar.value = true;
  const [userRes, fieldsRes] = await Promise.all([
    getTenantOrganizationUsers(item.id),
    getFields(),
  ]);
  state.userInfo = userRes.data;
  state.userInfo.extras = useCustomFields(state.userInfo?.extras, fieldsRes.data.custom_fields);
  detailsConfig.title = t('用户详情');
  detailsConfig.isShow = true;
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    if (enableLeave) {
      detailsConfig.isShow = false;
      hideSideBar();
    }
  } else {
    detailsConfig.isShow = false;
    hideSideBar();
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};
// 搜索用户名、姓名
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

  // :deep(.bk-modal-content) {
  //   overflow-y: auto;

  //   &::-webkit-scrollbar {
  //     width: 4px;
  //     background-color: transparent;
  //   }

  //   &::-webkit-scrollbar-thumb {
  //     background-color: #dcdee5;
  //     border-radius: 4px;
  //   }

  //   &:hover {
  //     &::-webkit-scrollbar-thumb {
  //       background-color: #979ba5;
  //     }
  //   }
  // }
}
</style>
