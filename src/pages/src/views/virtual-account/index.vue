<template>
  <div :class="['virtual-account-wrapper user-scroll-y', { 'has-alert': userStore.showAlert }]">
    <header>
      <div class="flex">
        <bk-button
          theme="primary"
          class="mr-[8px]"
          @click="handleClick('add')">
          <i class="user-icon icon-add-2 mr8" />
          {{ $t('新建') }}
        </bk-button>
      </div>
      <bk-input
        class="header-right"
        v-model="searchVal"
        :placeholder="$t('搜索用户名、全名')"
        type="search"
        clearable
        @enter="handleEnter"
        @clear="handleClear"
      />
    </header>
    <bk-table
      v-bkloading="{ loading: isLoading }"
      class="table-users"
      :min-height="150"
      :data="tableData"
      :border="['outer']"
      :pagination="pagination"
      :settings="settings"
      show-overflow-tooltip
      @select="handleSelect"
      @select-all="handleSelectAll"
      @page-limit-change="pageLimitChange"
      @page-value-change="pageCurrentChange"
    >
      <template #empty>
        <Empty
          :is-data-empty="isDataEmpty"
          :is-search-empty="isEmptySearch"
          :is-data-error="isDataError"
          @handle-empty="handleClear"
          @handle-update="initVirtualUsers"
        />
      </template>
      <template #prepend v-if="selectList.length">
        <div class="batch-operation">
          {{ $t('当前已选择') }}<span class="font-bold mx-[8px]">{{ selectList.length }}</span>{{ $t('条数据') }}
          <bk-button class="ml-[8px]" theme="primary" text>{{ $t('批量删除') }}</bk-button>
        </div>
      </template>
      <!-- 暂不支持批量操作 -->
      <!-- <bk-table-column type="selection" :width="80" align="center" /> -->
      <bk-table-column prop="username" :label="$t('用户名')">
        <template #default="{ row }">
          <bk-button text theme="primary" @click="handleClick('view', row.id)">{{ row.username }}</bk-button>
        </template>
      </bk-table-column>
      <bk-table-column prop="full_name" :label="$t('全名')" />
      <bk-table-column prop="app_codes" :label="$t('所属应用')">
        <template #default="{ row }">
          {{ row.app_codes?.length ? row.app_codes?.join(', ') : '--' }}
        </template>
      </bk-table-column>
      <bk-table-column prop="owners" :label="$t('账号责任人')">
        <template #default="{ row }">
          <bk-user-display-name :user-id="row.owners"></bk-user-display-name>
        </template>
      </bk-table-column>
      <bk-table-column prop="created_at" :label="$t('创建时间')">
        <template #default="{ row }">
          <span>{{ row?.created_at || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column prop="action" :label="$t('操作')" width="160">
        <template #default="{ row }">
          <bk-button class="mr-[8px]" theme="primary" text @click="handleClick('edit', row.id)">
            {{ $t('编辑') }}
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
    <!-- 新建编辑 -->
    <bk-sideslider
      :width="640"
      :is-show="detailsConfig.isShow"
      render-directive="if"
      :before-close="handleBeforeClose"
      quick-close
    >
      <template #header>
        <div class="flex justify-between w-full pr-[15px]">
          <div>{{ detailsConfig.title }}</div>
          <bk-button
            v-if="detailsConfig.type === 'view'"
            outline
            theme="primary"
            @click="handleClick('edit')">
            {{ $t('编辑') }}
          </bk-button>
        </div>
      </template>
      <EditDetails
        v-if="detailsConfig.type !== 'view'"
        :details-info="detailsInfo"
        @update-users="updateUsers"
        @handle-cancel-edit="handleCancelEdit" />
      <ViewDetails
        v-else
        :details-info="detailsInfo" />
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { inject, nextTick, onMounted, reactive, ref, watch  } from 'vue';

import EditDetails from './EditDetails.vue';
import ViewDetails from './ViewDetails.vue';

import Empty from '@/components/SearchEmpty.vue';
import { getVirtualUsers, getVirtualUsersDetail } from '@/http';
import { t } from '@/language/index';
import { useUser } from '@/store';

const userStore = useUser();

const editLeaveBefore = inject('editLeaveBefore');

const searchVal = ref('');
const isLoading = ref(false);
const tableData = ref([]);
const isDataEmpty = ref(false);
const isEmptySearch = ref(false);
const isDataError = ref(false);
const selectList = ref([]);

const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
});

onMounted(() => {
  initVirtualUsers();
});

// 获取虚拟用户列表
const initVirtualUsers = async () => {
  try {
    isLoading.value = true;
    isDataError.value = false;

    const params = {
      page: pagination.current,
      pageSize: pagination.limit,
      keyword: searchVal.value,
    };
    const res = await getVirtualUsers(params);
    if (res.data?.count === 0) {
      isDataEmpty.value = searchVal.value === '';
      isEmptySearch.value = searchVal.value !== '';
    }
    pagination.count = res.data?.count;
    tableData.value = res.data?.results;
  } catch (e) {
    console.warn(e);
    isDataError.value = true;
  } finally {
    isLoading.value = false;
  }
};

// 勾选数据行
const handleSelect = ({ row, checked }) => {
  checked ? selectList.value.push(row) : selectList.value = selectList.value.filter(item => item.id !== row.id);
};

// 勾选所有数据行
const handleSelectAll = ({ checked, data }) => {
  selectList.value = checked ? data : [];
};

// 新建/编辑信息
const detailsInfo = ref({
  username: '',
  full_name: '',
  app_codes: '',
  owners: [],
});

// 侧栏配置
const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
});

const settings = {
  fields: [
    {
      label: t('用户名'),
      field: 'username',
    },
    {
      label: t('全名'),
      field: 'full_name',
    },
    {
      label: t('所属应用'),
      field: 'app_codes',
    },
    {
      label: t('账号责任人'),
      field: 'owners',
    },
    {
      label: t('创建时间'),
      field: 'created_at',
    },
  ],
  checked: ['username', 'full_name', 'app_codes', 'owners', 'created_at'],
};

const enumData = {
  add: {
    title: t('新建虚拟账户'),
    type: 'add',
  },
  view: {
    title: t('账号详情'),
    type: 'view',
  },
  edit: {
    title: t('编辑虚拟账户'),
    type: 'edit',
  },
};
const isViewToEdit = ref(false);
watch(() => detailsConfig.isShow, (val) => {
  if (!val) {
    nextTick(() => {
      detailsInfo.value = {
        username: '',
        full_name: '',
        app_codes: '',
        owners: [],
      };
      isViewToEdit.value = false;
    });
  }
});

const handleClick = async (type: string, id?: string) => {
  if (type !== 'add' && !isViewToEdit.value) {
    const res = await getVirtualUsersDetail(id);
    detailsInfo.value = res.data;
    detailsInfo.value.app_codes = res.data?.app_codes.join(',');
    if (type === 'view') {
      isViewToEdit.value = true;
    }
  }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

// 更新虚拟用户列表
const updateUsers = (message: string) => {
  detailsConfig.isShow = false;
  window.changeInput = false;
  Message({ theme: 'success', message });
  initVirtualUsers();
};

const handleCancelEdit = () => {
  window.changeInput = false;
  detailsConfig.isShow = false;
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    detailsConfig.isShow = !enableLeave;
  } else {
    detailsConfig.isShow = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};
const handleEnter = () => {
  pagination.current = 1;
  initVirtualUsers();
};

const handleClear = () => {
  searchVal.value = '';
  pagination.current = 1;
  initVirtualUsers();
};

const pageLimitChange = (limit: number) => {
  pagination.limit = limit;
  pagination.current = 1;
  initVirtualUsers();
};

const pageCurrentChange = (current: number) => {
  pagination.current = current;
  initVirtualUsers();
};
</script>

<style lang="less" scoped>
.has-alert {
  height: calc(100vh - 92px) !important;
}

.virtual-account-wrapper {
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

  .batch-operation {
    height: 32px;
    line-height: 32px;
    text-align: center;
    background-color: #F0F1F5;
    border: 1px dashed #AFB0B2;
  }

  ::v-deep .table-users .bk-table-footer {
    padding-left: 18px;
    background: #fff;
  }
}
</style>
