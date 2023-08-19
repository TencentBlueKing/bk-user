<template>
  <div class="user-info-wrapper user-scroll-y">
    <header>
      <div>
        <bk-button theme="primary" class="mr8" @click="handleClick('add')">
          <i class="user-icon icon-add-2 mr8" />
          新建用户
        </bk-button>
        <bk-button class="mr8" style="width: 64px;">导入</bk-button>
        <!-- <bk-button>导出</bk-button> -->
      </div>
      <bk-input class="header-right" v-model="searchVal" type="search" />
    </header>
    <bk-table
      class="user-info-table"
      :columns="columns"
      :data="tableData"
      :border="['outer']"
      show-overflow-tooltip
    />
    <!-- 查看/编辑用户 -->
    <bk-sideslider
      ext-cls="details-edit-wrapper"
      :width="640"
      :isShow="detailsConfig.isShow"
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
            @click="handleClick('edit')">
            编辑
          </bk-button>
          <bk-button>重置</bk-button>
          <bk-button>删除</bk-button>
        </div>
      </template>
      <template #default>
        <ViewUser v-if="isView" />
        <EditUser v-else @handleCancelEdit="handleCancelEdit" />
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="tsx">
import { ref, reactive, computed, inject } from "vue";
import EditUser from "./EditUser.vue";
import ViewUser from "./ViewUser.vue";

const editLeaveBefore = inject("editLeaveBefore");
const searchVal = ref("");
const detailsConfig = reactive({
  isShow: false,
  title: "",
  type: "",
});

const enumData = {
  add: {
    title: "新建用户",
    type: "add",
  },
  view: {
    title: "用户详情",
    type: "view",
  },
  edit: {
    title: "编辑用户",
    type: "edit",
  },
};

const tableData = [
  {
    username: "Loretta Wolfe",
    full_name: "Larry Carlson",
    phone: "13122334455",
    email: "--",
    tissue: "--",
    enable: true,
  },
  {
    username: "Jeanette Stephens",
    full_name: "Bettie Ramos",
    phone: "13122334455",
    email: "--",
    tissue: "--",
    enable: true,
  },
];

const columns = [
  {
    label: "用户名",
    field: "username",
    render: ({ data }: { data: any }) => {
      return (
        <bk-button
          text
          theme="primary"
          onClick={handleClick.bind(this, "view", data)}
        >
          {data.username}
        </bk-button>
      );
    },
  },
  {
    label: "全名",
    field: "full_name",
  },
  {
    label: "手机号",
    field: "phone",
  },
  {
    label: "邮箱",
    field: "email",
  },
  {
    label: "所属组织",
    field: "tissue",
  },
  {
    label: "启/停",
    field: "enable",
    render: ({ data }: { data: any }) => {
      return <bk-switcher value={data.enable} theme="primary"></bk-switcher>;
    },
  },
  {
    label: "操作",
    field: "",
    render: ({ data }: { data: any }) => {
      return (
        <div>
          <bk-button
            theme="primary"
            text
            class="mr8"
            onClick={handleClick.bind(this, "edit", data)}
          >
            编辑
          </bk-button>
          <bk-button theme="primary" text class="mr8">
            重置密码
          </bk-button>
          <bk-button theme="primary" text>
            删除
          </bk-button>
        </div>
      );
    },
  },
];

const isView = computed(() => detailsConfig.type === "view");

const handleClick = (type: string, item: any) => {
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
      width: 320px;
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
