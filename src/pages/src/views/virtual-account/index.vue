<template>
  <div :class="['virtual-account-wrapper user-scroll-y', { 'has-alert': userStore.showAlert }]">
    <header>
      <bk-button theme="primary" @click="handleClick('add')">
        <i class="user-icon icon-add-2 mr8" />
        {{ $t('新建') }}
      </bk-button>
      <bk-input
        class="header-right"
        v-model="searchVal"
        :placeholder="$t('搜索用户名、姓名')"
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
      <bk-table-column prop="id" :label="$t('用户ID')">
        <template #default="{ row }">
          <span
            class="cursor-pointer"
            @mouseenter="row.isShow = true"
            @mouseleave="row.isShow = false"
            @click="copy(row.id)"
          >
            {{ row.id }}
            <i v-if="row.isShow" class="user-icon icon-copy text-[#3A84FF] text-[14px]" />
          </span>
        </template>
      </bk-table-column>
      <bk-table-column prop="username" :label="$t('用户名')" />
      <bk-table-column prop="full_name" :label="$t('姓名')" />
      <bk-table-column prop="email" :label="$t('邮箱')">
        <template #default="{ row }">{{ row.email || '--' }}</template>
      </bk-table-column>
      <bk-table-column prop="phone" :label="$t('手机号')">
        <template #default="{ row }">{{ row.phone || '--' }}</template>
      </bk-table-column>
      <bk-table-column :label="$t('操作')" width="150">
        <template #default="{ row }">
          <bk-button class="mr-[8px]" theme="primary" text @click="handleClick('edit', row.id)">
            {{ $t('编辑') }}
          </bk-button>
          <bk-button theme="primary" text @click="handleDelete(row)">{{ $t('删除') }}</bk-button>
        </template>
      </bk-table-column>
    </bk-table>
    <!-- 新建编辑 -->
    <bk-sideslider
      :width="640"
      :is-show="detailsConfig.isShow"
      :title="detailsConfig.title"
      render-directive="if"
      :before-close="handleBeforeClose"
      quick-close
    >
      <EditDetails
        :details-info="detailsInfo"
        @update-users="updateUsers"
        @handle-cancel-edit="handleCancelEdit" />
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { InfoBox, Message } from 'bkui-vue';
import { inject, nextTick, onMounted, reactive, ref, watch } from 'vue';

import EditDetails from './EditDetails.vue';

import Empty from '@/components/Empty.vue';
import { deleteVirtualUsers, getVirtualUsers, getVirtualUsersDetail } from '@/http';
import { t } from '@/language/index';
import { useUser } from '@/store';
import { copy } from '@/utils';

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
  email: '',
  phone: '',
  phone_country_code: '86',
});

// 侧栏配置
const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
});

const enumData = {
  add: {
    title: t('新增用户'),
    type: 'add',
  },
  edit: {
    title: t('编辑用户'),
    type: 'edit',
  },
};

watch(() => detailsConfig.isShow, (val) => {
  if (!val) {
    nextTick(() => {
      detailsInfo.value = {
        username: '',
        full_name: '',
        email: '',
        phone: '',
        phone_country_code: '86',
      };
    });
  }
});

const handleClick = async (type: string, id?: string) => {
  if (type !== 'add') {
    const res = await getVirtualUsersDetail(id);
    detailsInfo.value = res.data;
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

const handleDelete = (item: any) => {
  InfoBox({
    width: 400,
    title: `${t('确认删除')} ${item.username} ${t('用户')}？`,
    confirmText: t('删除'),
    onConfirm: async () => {
      await deleteVirtualUsers(item.id);
      initVirtualUsers();
      Message({ theme: 'success', message: t('删除成功') });
    },
  });
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
