<template>
  <div class="group-details-wrapper user-scroll-y">
    <div class="main-content">
      <div class="content-search">
        <bk-button theme="primary" @click="handleClick('add')">
          <i class="user-icon icon-add-2 mr8" />
          新建公司
        </bk-button>
        <bk-input
          class="content-search-input"
          v-model="searchName"
          placeholder="搜索公司名、姓名"
          type="search"
          clearable
          @enter="handleEnter"
          @clear="fetchTenantsList"
        />
      </div>
      <bk-loading :loading="state.tableLoading">
        <bk-table
          class="content-table"
          :data="state.list"
          show-overflow-tooltip>
          <template #empty>
            <Empty
              :is-data-empty="state.isTableDataEmpty"
              :is-search-empty="state.isEmptySearch"
              :is-data-error="state.isTableDataError"
              @handleEmpty="fetchTenantsList"
              @handleUpdate="fetchTenantsList"
            />
          </template>
          <bk-table-column prop="name" label="公司名">
            <template #default="{ row, index }">
              <div class="item-name">
                <img v-if="row.logo" :src="row.logo" />
                <span v-else class="logo" :style="`background-color: ${LOGO_COLOR[index]}`">
                  {{ convertLogo(row.name) }}
                </span>
                <bk-button
                  text
                  theme="primary"
                  @click="handleClick('view', row)"
                >
                  {{ row.name }}
                </bk-button>
              </div>
            </template>
          </bk-table-column>
          <bk-table-column prop="id" label="公司ID"></bk-table-column>
          <bk-table-column prop="managers" label="公司管理员">
            <template #default="{ row }">
              <bk-tag v-for="(item, index) in row.managers" :key="index">{{ item.username }}</bk-tag>
            </template>
          </bk-table-column>
          <bk-table-column prop="data_sources" label="已绑定数据源">
            <template #default="{ row }">
              <span>{{ convertFormat(row.data_sources) }}</span>
            </template>
          </bk-table-column>
          <bk-table-column prop="created_at" label="创建时间" />
          <bk-table-column label="操作">
            <template #default="{ row }">
              <bk-button
                text
                theme="primary"
                style="margin-right: 8px;"
                @click="handleClick('edit', row)"
              >
                编辑
              </bk-button>
            </template>
          </bk-table-column>
        </bk-table>
      </bk-loading>
    </div>
    <bk-sideslider
      :ext-cls="['details-wrapper', { 'details-edit-wrapper': !isView }]"
      :width="isView ? 640 : 960"
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
            @click="handleClick('edit', state.tenantsData)"
          >编辑</bk-button
          >
        </div>
      </template>
      <template #default>
        <ViewDetails v-if="isView" :tenants-data="state.tenantsData" />
        <OperationDetails
          v-else
          :type="detailsConfig.type"
          :tenants-data="state.tenantsData"
          @handleCancelEdit="handleCancelEdit"
          @updateTenantsList="updateTenantsList"
        />
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, inject, reactive, ref, watch } from 'vue';

import OperationDetails from './OperationDetails.vue';
import ViewDetails from './ViewDetails.vue';

import Empty from '@/components/Empty.vue';
import {
  getTenantDetails,
  getTenants,
  searchTenants,
} from '@/http/tenantsFiles';
import { useMainViewStore } from '@/store/mainView';
import { LOGO_COLOR } from '@/utils';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const editLeaveBefore = inject('editLeaveBefore');
const searchName = ref('');
const state = reactive({
  list: [],
  tableLoading: true,
  // 搜索结果为空
  isEmptySearch: false,
  // 表格请求出错
  isTableDataError: false,
  // 表格请求结果为空
  isTableDataEmpty: false,
  // 租户详情数据
  tenantsData: {
    name: '',
    id: '',
    feature_flags: {
      user_number_visible: true,
    },
    logo: '',
    managers: [
      {
        username: '',
        full_name: '',
        email: '',
        phone: '',
        phone_country_code: '86',
      },
    ],
  },
});
const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
});
const enumData = {
  view: {
    title: '公司详情',
    type: 'view',
  },
  add: {
    title: '新建公司',
    type: 'add',
  },
  edit: {
    title: '编辑公司',
    type: 'edit',
  },
};

watch(
  () => detailsConfig.isShow,
  () => {
    if (!detailsConfig.isShow) {
      state.tenantsData = {
        name: '',
        id: '',
        feature_flags: {
          user_number_visible: true,
        },
        logo: '',
        managers: [
          {
            username: '',
            full_name: '',
            email: '',
            phone: '',
            phone_country_code: '86',
          },
        ],
        // password_settings: {
        //   init_password: "",
        //   init_password_method: "fixed_password",
        //   init_notify_method: [],
        //   init_sms_config: {},
        //   init_mail_config: {},
        // },
      };
    }
  },
);

const isView = computed(() => detailsConfig.type === 'view');

const convertLogo = name => name?.charAt(0).toUpperCase();
const convertFormat = name => name?.map(item => item?.name).join(',') || '--';

const handleClick = async (type: string, item?: any) => {
  if (type !== 'add') {
    await getTenantDetails(item.id).then((res: any) => {
      state.tenantsData = res.data;
    });
  }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

const handleCancelEdit = async () => {
  window.changeInput = false;
  if (detailsConfig.type === 'add') {
    detailsConfig.isShow = false;
  } else {
    detailsConfig.type = 'view';
    detailsConfig.title = '公司详情';
    window.changeInput = false;
  }
};
// 获取租户列表
const fetchTenantsList = () => {
  searchName.value = '';
  state.tableLoading = true;
  state.isTableDataEmpty = false;
  state.isEmptySearch = false;
  state.isTableDataError = false;
  getTenants()
    .then((res: any) => {
      if (res.data.length === 0) {
        state.isTableDataEmpty = true;
      }
      state.list = res.data;
      state.tableLoading = false;
    })
    .catch(() => {
      state.isTableDataError = true;
      state.tableLoading = false;
    });
};
// 初始化加载
fetchTenantsList();
// 搜索租户列表
const handleEnter = () => {
  state.tableLoading = true;
  searchTenants(searchName.value)
    .then((res: any) => {
      if (res.data.length === 0) {
        state.isEmptySearch = true;
      }
      state.list = res.data;
      state.tableLoading = false;
    })
    .catch(() => {
      state.isTableDataError = true;
      state.tableLoading = false;
    });
};
// 更新租户列表
const updateTenantsList = (text) => {
  detailsConfig.isShow = false;
  window.changeInput = false;
  fetchTenantsList();
  Message({
    theme: 'success',
    message: text,
  });
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
</script>

<style lang="less" scoped>
.group-details-wrapper {
  width: 100%;
  height: calc(100vh - 104px);
  padding: 24px;

  .main-content {
    .content-search {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .content-search-input {
        width: 400px;
      }
    }

    :deep(.bk-table) {
      .item-name {
        display: flex;
        align-items: center;
        height: 42px;
        line-height: 42px;

        img {
          width: 16px;
          height: 16px;
          margin-right: 8px;
          border: 1px solid #C4C6CC;
          border-radius: 50%;
          object-fit: contain;
        }

        .logo {
          display: inline-block;
          width: 16px;
          margin-right: 8px;
          font-size: 12px;
          font-weight: 700;
          line-height: 16px;
          color: #fff;
          text-align: center;
          background-color: #C4C6CC;
          border-radius: 4px;
          flex-shrink: 0;
        }
      }
    }
  }
}

.details-wrapper {
  :deep(.bk-sideslider-title) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px 0 50px !important;

    .bk-button {
      padding: 5px 17px !important;
    }
  }
}

.details-edit-wrapper {
  :deep(.bk-modal-content) {
    height: calc(100vh - 106px);
    background: #f5f7fa;
  }
}
</style>
