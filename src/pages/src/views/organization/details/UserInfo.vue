<template>
  <div class="user-info-wrapper user-scroll-y">
    <header>
      <bk-checkbox v-model="isSearchCurrentDepartment">
        仅显示本级用户（<span>23</span>）
      </bk-checkbox>
      <bk-input
        class="header-right"
        v-model="searchVal"
        placeholder="搜索用户名、全名"
        type="search"
      />
    </header>
    <bk-table
      class="user-info-table"
      :columns="columns"
      :data="tableData"
      :pagination="pagination"
      settings
      :border="['outer']"
    />
    <!-- 查看/编辑用户 -->
    <bk-sideslider
      ext-cls="details-edit-wrapper"
      :width="640"
      v-model:isShow="detailsConfig.isShow"
      :title="detailsConfig.title"
      quick-close
    >
      <template #header>
        <span>{{ detailsConfig.title }}</span>
      </template>
      <EditUser v-if="!isView" />
      <template #footer v-if="!isView">
        <bk-button theme="primary">
          保存
        </bk-button>
        <bk-button>
          取消
        </bk-button>
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="tsx">
import { Plus, AngleDown, AngleUp } from "bkui-vue/lib/icon";
import { ref, reactive, computed } from "vue";
import EditUser from "./EditUser.vue";
import { statusIcon } from "@/utils";

const isSearchCurrentDepartment = ref(false);
const searchVal = ref("");

const detailsConfig = reactive({
  isShow: false,
  title: "",
  type: "",
});

const tableData = [
  {
    username: "lululi",
    display_name: "lululi",
    status: "normal",
    email: "lululi@qq.com",
    telephone: "18123456789",
    department_name: "总公司",
  },
  {
    username: "helloword",
    display_name: "helloword",
    status: "disabled",
    email: "helloword@qq.com",
    telephone: "18123456789",
    department_name: "总公司",
  },
];

const columns = [
  {
    label: "用户名",
    field: "username",
    render: ({ data }: { data: any }) => {
      return (
        <bk-button text theme="primary" onClick={handleClick.bind(this, 'view', data)}>
          { data.username }
        </bk-button>
      );
    },
  },
  {
    label: "全名",
    field: "display_name",
  },
  {
    label: "账号状态",
    field: "status",
    render: ({ data }: { data: any }) => {
      return (
        <div>
          <img src={statusIcon[data.status].icon} class="account-status-icon" />
          <span>{ statusIcon[data.status].text }</span>
        </div>
      );
    },
  },
  {
    label: "邮箱",
    field: "email",
  },
  {
    label: "手机号",
    field: "telephone",
  },
  {
    label: "组织",
    field: "department_name",
  },
  {
    label: "操作",
    field: "",
    render: ({ data }: { data: any }) => {
      return (
        <bk-button text theme="primary" onClick={handleClick.bind(this, 'edit', data)}>
          编辑
        </bk-button>
      );
    },
  },
];

const pagination = {
  conut: tableData.length,
  limit: 10,
};

const enumData = {
  "view": {
    title: "用户详情",
    type: "view",
  },
  "edit": {
    title: "编辑用户",
    type: "edit",
  },
};

const isView = computed(() => detailsConfig.type === 'view');

const handleClick = (type: string, item: any) => {
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};
</script>

<style lang="less" scoped>
.user-info-wrapper {
  width: 100%;
  padding: 24px;
  height: calc(100vh - 140px);
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
      vertical-align: middle;
      margin-right: 5px;
    }
  }
}
.details-edit-wrapper {
  :deep(.bk-modal-content) {
    height: calc(100vh - 106px);
    padding: 28px 40px 40px;
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
