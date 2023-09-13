<template>
  <bk-loading :loading="isLoading" class="user-info-wrapper user-scroll-y">
    <header>
      <div>
        <bk-button theme="primary" class="mr8" @click="handleClick('add')">
          <i class="user-icon icon-add-2 mr8" />
          新建用户
        </bk-button>
        <bk-button class="mr8" style="width: 64px;">导入</bk-button>
        <!-- <bk-button>导出</bk-button> -->
      </div>
      <bk-input
        class="header-right"
        v-model="searchVal"
        placeholder="搜索公司名、姓名"
        type="search"
        clearable
        @enter="handleEnter"
        @clear="handleClear" />
    </header>
    <bk-table
      class="user-info-table"
      :data="users"
      :border="['outer']"
      remote-pagination
      :pagination="pagination"
      show-overflow-tooltip
      @page-limit-change="pageLimitChange"
      @page-value-change="pageCurrentChange"
    >
      <template #empty>
        <Empty
          :is-data-empty="isDataEmpty"
          :is-search-empty="isEmptySearch"
          :is-data-error="isDataError"
          @handleEmpty="handleClear"
          @handleUpdate="handleClear"
        />
      </template>
      <bk-table-column prop="username" label="用户名">
        <template #default="{ row }">
          <bk-button text theme="primary" @click="handleClick('view', row)">
            {{ row.username }}
          </bk-button>
        </template>
      </bk-table-column>
      <bk-table-column prop="full_name" label="全名"></bk-table-column>
      <bk-table-column prop="phone" label="手机号"></bk-table-column>
      <bk-table-column prop="email" label="邮箱"></bk-table-column>
      <bk-table-column prop="departments" label="所属组织">
        <template #default="{ row }">
          <span>{{ formatConvert(row.departments) }}</span>
        </template>
      </bk-table-column>
      <bk-table-column label="操作">
        <template #default="{ row }">
          <bk-button
            theme="primary"
            text
            class="mr8"
            @click="handleClick('edit', row)"
          >
            编辑
          </bk-button>
          <!-- <bk-button theme="primary" text class="mr8">
            重置密码
          </bk-button>
          <bk-button theme="primary" text>
            删除
          </bk-button> -->
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
        <div v-if="isView">
          <bk-button
            outline
            theme="primary"
            @click="handleClick('edit', detailsConfig)">
            编辑
          </bk-button>
          <!-- <bk-button>重置</bk-button>
          <bk-button>删除</bk-button> -->
        </div>
      </template>
      <template #default>
        <ViewUser v-if="isView" :users-data="detailsConfig.usersData" />
        <EditUser
          v-else
          :type="detailsConfig.type"
          :users-data="detailsConfig.usersData"
          :current-id="detailsConfig.id"
          :data-source-id="dataSourceId"
          @handleCancelEdit="handleCancelEdit"
          @updateUsers="updateUsers" />
      </template>
    </bk-sideslider>
  </bk-loading>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, inject, onMounted, reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import EditUser from './EditUser.vue';
import ViewUser from './ViewUser.vue';

import Empty from '@/components/Empty.vue';
import { getDataSourceUserDetails, getDataSourceUsers } from '@/http/dataSourceFiles';

const route = useRoute();

const currentId = computed(() => Number(route.params.id));

const editLeaveBefore = inject('editLeaveBefore');
const searchVal = ref('');
const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
  usersData: {
    username: '',
    full_name: '',
    department_ids: [],
    leader_ids: [],
    email: '',
    phone_country_code: '+86',
    phone: '',
    logo: '',
  },
  id: '',
});

const enumData = {
  add: {
    title: '新建用户',
    type: 'add',
  },
  view: {
    title: '用户详情',
    type: 'view',
  },
  edit: {
    title: '编辑用户',
    type: 'edit',
  },
};

watch(
  () => detailsConfig.isShow,
  () => {
    if (!detailsConfig.isShow) {
      detailsConfig.usersData = {
        username: '',
        full_name: '',
        department_ids: [],
        leader_ids: [],
        email: '',
        phone_country_code: '+86',
        phone: '',
        logo: '',
      };
    }
  },
);

const isView = computed(() => detailsConfig.type === 'view');

onMounted(() => {
  getUsers();
});

const isLoading = ref(false);
const isDataEmpty = ref(false);
const isEmptySearch = ref(false);
const isDataError = ref(false);

const params = reactive({
  id: currentId.value,
  username: '',
  page: 1,
  pageSize: 10,
});

const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
});

const users = ref([]);

const getUsers = async () => {
  try {
    isLoading.value = true;
    isDataEmpty.value = false;
    isEmptySearch.value = false;
    isDataError.value = false;
    const res = await getDataSourceUsers(params);
    if (res.data.count === 0) {
      params.username === '' ? isDataEmpty.value = true : isEmptySearch.value = true;
    }
    pagination.count = res.data.count;
    users.value = res.data.results;
  } catch (error) {
    isDataError.value = true;
  } finally {
    isLoading.value = false;
  }
};

const handleClick = async (type: string, item?: any) => {
  if (type !== 'add') {
    const res = await getDataSourceUserDetails(item.id);
    detailsConfig.usersData = res.data;
    detailsConfig.id = item.id;
  }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

const handleCancelEdit = () => {
  window.changeInput = false;
  if (detailsConfig.type === 'add') {
    detailsConfig.isShow = false;
  } else {
    detailsConfig.type = 'view';
    detailsConfig.title = '公司详情';
    window.changeInput = false;
  }
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

const formatConvert = (data) => {
  const departments = data?.map(item => item.name).join('/') || '--';
  return departments;
};

const updateUsers = (value, text) => {
  detailsConfig.isShow = false;
  params.username = value;
  getUsers();
  Message({
    theme: 'success',
    message: text,
  });
};

const handleEnter = () => {
  params.username = searchVal.value;
  getUsers();
};

const handleClear = () => {
  searchVal.value = '';
  params.username = '';
  getUsers();
};

const pageLimitChange = (limit) => {
  pagination.limit = limit;
  params.pageSize = limit;
  getUsers();
};
const pageCurrentChange = (current) => {
  pagination.current = current;
  params.page = current;
  getUsers();
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
      width: 320px;
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
