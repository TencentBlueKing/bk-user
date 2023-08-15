<template>
  <div class="group-details-wrapper user-scroll-y">
    <div class="main-content">
      <div class="content-search">
        <bk-button theme="primary" @click="handleClick('add', '')">
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
          :columns="columns"
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
        </bk-table>
      </bk-loading>
    </div>
    <bk-sideslider
      :ext-cls="['details-wrapper', { 'details-edit-wrapper': !isView }]"
      :width="isView ? 640 : 960"
      :isShow="detailsConfig.isShow"
      :title="detailsConfig.title"
      :before-close="handleBeforeClose"
      quick-close
    >
      <template #header>
        <span>{{ detailsConfig.title }}</span>
        <div v-if="isView">
          <bk-button @click="handleClick('edit', state.tenantsData)"
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

<script setup lang="tsx">
import { ref, reactive, watch, computed, nextTick, inject } from "vue";
import {
  getTenants,
  searchTenants,
  getTenantDetails,
} from "@/http/tenantsFiles";
import { logoColor } from "@/utils";
import moment from "moment";
import InfoBox from "bkui-vue/lib/info-box";
import { useMainViewStore } from "@/store/mainView";
import Empty from "@/components/Empty.vue";
import ViewDetails from "./ViewDetails.vue";
import OperationDetails from "./OperationDetails.vue";

const store = useMainViewStore();
store.customBreadcrumbs = false;

const editLeaveBefore = inject('editLeaveBefore');
const searchName = ref("");
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
    name: "",
    id: "",
    feature_flags: {
      user_number_visible: true,
    },
    logo: "",
    managers: [
      {
        username: "",
        full_name: "",
        email: "",
        phone: "",
        phone_country_code: "86",
      },
    ],
  },
});
const columns = [
  {
    label: "公司名",
    field: "name",
    render: ({ data, index }: { data: any, index: any }) => {
      return (
        <div class="item-name">
          {
            data.logo
              ? <img src={data.logo} />
              : <span class="logo" style={`background-color: ${logoColor[index]}`}>
                  {data.name.charAt(0).toUpperCase()}
                </span>
          }
          <bk-button
            text
            theme="primary"
            onClick={handleClick.bind(this, "view", data)}
          >
            {data.name}
          </bk-button>
        </div>
      );
    },
  },
  {
    label: "公司ID",
    field: "id",
  },
  {
    label: "公司管理员",
    field: "managers",
    render: ({ data }: { data: any }) =>
      data.managers.map((item: any) => <bk-tag>{item.username}</bk-tag>),
  },
  {
    label: "已绑定数据源",
    field: "data_sources",
    render: ({ data }: { data: any }) => {
      const list = data.data_sources.map((item: any) => item.name);
      return <span>{list.join(",")}</span>
    }
  },
  {
    label: "创建时间",
    field: "create_at",
    render: ({ data }: { data: any }) => (
      <span>{moment(data.create_time).format("YYYY-MM-DD HH:mm:ss")}</span>
    ),
  },
  {
    label: "操作",
    field: "",
    width: 80,
    render: ({ data }: { data: any }) => {
      return (
        <div>
          <bk-button
            text
            theme="primary"
            style="margin-right: 8px;"
            onClick={handleClick.bind(this, "edit", data)}
          >
            编辑
          </bk-button>
        </div>
      );
    },
  },
];
const detailsConfig = reactive({
  isShow: false,
  title: "",
  type: "",
});
const enumData = {
  view: {
    title: "公司详情",
    type: "view",
  },
  add: {
    title: "新建公司",
    type: "add",
  },
  edit: {
    title: "编辑公司",
    type: "edit",
  },
};

watch(
  () => detailsConfig.isShow,
  () => {
    if (!detailsConfig.isShow) {
      state.tenantsData = {
        name: "",
        id: "",
        feature_flags: {
          user_number_visible: true,
        },
        logo: "",
        managers: [
          {
            username: "",
            display_name: "",
            email: "",
            telephone: "",
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
  }
);

const isView = computed(() => detailsConfig.type === "view");

const handleClick = async (type: string, item: any) => {
  if (type !== "add") {
    await getTenantDetails(item.id).then((res: any) => {
      state.tenantsData = res.data;
    });
  }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

const handleCancelEdit = async () => {
  if (detailsConfig.type === "add") {
    detailsConfig.isShow = false;
  } else {
    detailsConfig.type = "view";
    detailsConfig.title = "公司详情";
    window.changeInput = false;
  }
};
// 获取租户列表
const fetchTenantsList = () => {
  searchName.value = "";
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
const updateTenantsList = () => {
  detailsConfig.isShow = false;
  fetchTenantsList();
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
        }
        .logo {
          display: inline-block;
          width: 16px;
          line-height: 16px;
          text-align: center;
          font-weight: 700;
          color: #fff;
          background-color: #C4C6CC;
          border-radius: 4px;
          flex-shrink: 0;
          font-size: 12px;
          margin-right: 8px;
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
    background: #f5f7fa;
    height: calc(100vh - 106px);
  }
}
</style>
