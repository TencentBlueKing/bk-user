<template>
  <div class="user-info-wrapper user-scroll-y">
    <header>
      <div>
        <bk-button theme="primary" class="mr8">
          <i class="user-icon icon-add-2 mr8" />
          新建用户
        </bk-button>
        <bk-button class="mr8">导入</bk-button>
        <!-- <bk-button>导出</bk-button> -->
      </div>
      <bk-input
        class="header-right"
        v-model="searchVal"
        type="search"
      />
    </header>
    <bk-table
      class="user-info-table"
      :columns="columns"
      :data="tableData"
      :border="['outer']"
      show-overflow-tooltip
    />
  </div>
</template>

<script setup lang="tsx">
import { ref } from "vue";

const searchVal = ref("");
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
        <bk-button text theme="primary">
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
      return (
        <bk-switcher value={data.enable} theme="primary"></bk-switcher>
      );
    },
  },
  {
    label: "操作",
    field: "",
    render: ({ data }: { data: any }) => {
      return (
        <div>
          <bk-button theme="primary" text class="mr8">编辑</bk-button>
          <bk-button theme="primary" text class="mr8">重置密码</bk-button>
          <bk-button theme="primary" text>删除</bk-button>
        </div>
      );
    }
  },
];
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
</style>
