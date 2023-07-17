<template>
  <div class="group-details-wrapper user-scroll-y">
    <div class="main-content-bottom">
      <div class="content-search">
        <bk-button theme="primary" @click="handleClick('add', '')">
          <Plus width="1.5em" height="1.5em" />
          新建公司
        </bk-button>
        <bk-input
          class="content-search-input"
          v-model="searchVal"
          placeholder="搜索公司名、全名"
          type="search"
        />
      </div>
      <div class="content-table">
        <bk-table :data="tableData" :columns="columns" show-overflow-tooltip />
      </div>
    </div>
    <bk-sideslider
      :ext-cls="[
        'details-wrapper',
        { 'details-edit-wrapper': !isView }
      ]"
      :width="isView ? 640 : 960"
      v-model:isShow="detailsConfig.isShow"
      :title="detailsConfig.title"
      quick-close
    >
      <template #header>
        <span>{{ detailsConfig.title }}</span>
        <div v-if="isView">
          <bk-button @click="handleClick('edit', detailsConfig.basicInfo)"
            >编辑</bk-button
          >
        </div>
      </template>
      <template #default>
        <ViewDetails
          v-if="isView"
          :basic-info="detailsConfig.basicInfo"
          :user-data="userData"
        />
        <OperationDetails
          v-else
          :basic-info="detailsConfig.basicInfo"
          :user-data="detailsConfig.userData"
          :init-password="detailsConfig.initPassword"
        />
      </template>
      <template #footer v-if="!isView">
        <bk-button theme="primary">
          提交
        </bk-button>
        <bk-button @click="handleCancelEdit">
          取消
        </bk-button>
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="tsx">
import { Plus } from "bkui-vue/lib/icon";
import { reactive, watch, computed } from "vue";
import OrganizationTree from "./tree/OrganizationTree.vue";
import ViewDetails from "./ViewDetails.vue";
import OperationDetails from "./OperationDetails.vue";
import { InfoBox } from "bkui-vue";

const searchVal = "";
const tableData = [
  {
    name: "总公司",
    id: "1",
    num: "123",
    admin: ["admin", "v_yutyi"],
    data_source: "蓝鲸外包员工，蓝鲸内部员工",
    create_time: "2023-03-15",
    isShow: true,
  },
  {
    name: "test",
    id: "2",
    num: "234",
    admin: ["v_yutyi"],
    data_source: "蓝鲸外包员工，蓝鲸内部员工",
    create_time: "2023-04-15",
    isShow: false,
  },
];
const columns = [
  {
    label: "公司名",
    field: "name",
    render: ({ data }: { data: any }) => {
      return (
        <bk-button
          text
          theme="primary"
          onClick={handleClick.bind(this, 'view', data)}
        >
          {data.name}
        </bk-button>
      );
    },
  },
  {
    label: "公司ID",
    field: "id",
  },
  {
    label: "公司人数",
    field: "num",
  },
  {
    label: "公司管理员",
    field: "admin",
    render: ({ data }: { data: any }) =>
      data.admin.map((item: string) => {
        return <bk-tag>{item}</bk-tag>;
      }),
  },
  {
    label: "已绑定数据源",
    field: "data_source",
  },
  {
    label: "创建时间",
    field: "create_time",
  },
  {
    label: "操作",
    field: "",
    render: ({ data }: { data: any }) => {
      return (
        <div>
          <bk-button
            text
            theme="primary"
            style="margin-right: 8px;"
            onClick={handleClick.bind(this, 'edit', data)}
          >
            编辑
          </bk-button>
        </div>
      );
    },
  },
];
const userData = [
  {
    username: "admin-1",
    display_name: "admin-1",
    email: "admin-1@qq.com",
    telephone: "13911112222",
  },
  {
    username: "admin-2",
    display_name: "admin-2",
    email: "admin-2@qq.com",
    telephone: "13911112222",
  },
];
const detailsConfig = reactive({
  isShow: false,
  title: "",
  type: "",
  basicInfo: {
    name: "",
    id: "",
    isShow: true,
  },
  userData: [
    {
      username: "",
      display_name: "",
      email: "",
      telephone: "",
    },
  ],
  initPassword: {
    mode: "custom",
    password: "",
  },
});
const enumData = {
  "view": {
    title: "公司详情",
    type: "view",
  },
  "add": {
    title: "新建公司",
    type: "add",
  },
  "edit": {
    title: "编辑公司",
    type: "edit",
  },
};

watch(() => detailsConfig.isShow, () => {
    if (!detailsConfig.isShow) {
      detailsConfig.basicInfo = {
        name: "",
        id: "",
        isShow: true,
      };
    }
  }
);
watch(() => detailsConfig.type, () => {
    if (detailsConfig.type === "edit") {
      detailsConfig.userData = userData;
    }
  }
);
const isView = computed(() => detailsConfig.type === 'view');

const handleClick = (type: string, item: any) => {
  if (item) {
    detailsConfig.basicInfo = item;
  }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

const handleCancelEdit = () => {
  if (detailsConfig.type === "add") {
    detailsConfig.isShow = false;
  } else {
    detailsConfig.type = "view";
    detailsConfig.title = "公司详情";
  }
};
</script>

<style lang="less" scoped>
.group-details-wrapper {
  width: 100%;
  height: calc(100vh - 104px);
  padding: 24px;

  .main-content-bottom {
    .content-search {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      .content-search-input {
        width: 400px;
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
  :deep(.bk-sideslider-footer) {
    padding: 0 24px;
    background: #fafbfd;
    .bk-button {
      width: 88px;
      margin-right: 8px;
    }
  }
}
</style>
