<template>
  <div class="field-setting-content user-scroll-y">
    <bk-button class="add-field" theme="primary">
      <Plus style="font-size: 18px;" />
      添加字段
    </bk-button>
    <bk-table
      class="field-setting-table"
      :columns="columns"
      :data="tableData"
      row-key="id"
      :border="['outer']"
      settings
      show-overflow-tooltip
      :pagination="pagination"
    />
  </div>
</template>

<script setup lang="tsx">
import { ref, reactive, nextTick } from "vue";
import { Plus } from "bkui-vue/lib/icon";
import Sortable from "sortablejs";
import { useMainViewStore } from "@/store/mainView";

const store = useMainViewStore();
store.customBreadcrumbs = false;
const tableData: any = [
  {
    builtin: true,
    configurable: false,
    default: "",
    display_name: "用户名",
    editable: false,
    enabled: true,
    id: 1,
    key: "username",
    name: "用户名",
    order: 1,
    require: true,
    type: "string",
    unique: true,
    visible: true,
  },
  {
    builtin: true,
    configurable: true,
    default: "",
    display_name: "全名",
    editable: true,
    enabled: true,
    id: 2,
    key: "display_name",
    name: "全名",
    order: 2,
    require: true,
    type: "string",
    unique: false,
    visible: true,
  },
  {
    builtin: true,
    configurable: false,
    default: "",
    display_name: "邮箱",
    editable: true,
    enabled: true,
    id: 3,
    key: "email",
    name: "邮箱",
    order: 3,
    require: true,
    type: "string",
    unique: false,
    visible: true,
  },
];
const columns = [
  {
    label: "字段名称",
    field: "name",
    render: ({ data }: { data: any }) => {
      return (
        <div class="field-name">
          <i class="user-icon icon-drag move" />
          <span class="name">{data.name}</span>
          {data.builtin ? <bk-tag theme="info">内置</bk-tag> : ""}
        </div>
      );
    },
  },
  {
    label: "英文标识",
    field: "key",
  },
  {
    label: "字段类型",
    field: "type",
  },
  {
    label: "是否必填",
    field: "require",
    render: ({ data }: { data: any }) => fieldStatus(data.require),
  },
  {
    label: "是否唯一",
    field: "unique",
    render: ({ data }: { data: any }) => fieldStatus(data.unique),
  },
  {
    label: "是否可编辑",
    field: "editable",
    render: ({ data }: { data: any }) => fieldStatus(data.editable),
  },
  {
    label: "操作",
    field: "",
    render: ({ data }: { data: any }) => {
      return (
        <div>
          <bk-button text theme="primary" class="mr8">
            编辑
          </bk-button>
          <bk-button text theme="primary">
            删除
          </bk-button>
        </div>
      );
    },
  },
];

const pagination = reactive({
  count: tableData.length,
  limit: 10,
  limitList: [10, 20, 50, 100],
});

// 展示字段状态
const fieldStatus = (type: boolean) => {
  if (type) {
    return <i class="user-icon icon-duihao-i" />;
  }
};

const initSortable = (className: string) => {
  // 获取表格row的父节点
  const table = document.querySelector(
    "." + className + " .bk-table-body tbody"
  );
  // 创建拖拽实例
  Sortable.create(table, {
    handle: ".move",
    group: table,
    ghostClass: "blue-background-class",
    animation: 150,
    onUpdate: (event: any) => {
      console.log("event", event);
    },
  });
};

nextTick(() => {
  initSortable("field-setting-table");
});
</script>

<style lang="less" scoped>
.field-setting-content {
  padding: 24px;
  height: calc(100vh - 104px);
  .add-field {
    margin-bottom: 16px;
  }
  :deep(.field-setting-table) {
    .field-name {
      .move {
        color: #c8c8c8;
        font-size: 16px;
        cursor: move;
      }
      .name {
        color: #63656e;
        margin: 0 8px;
      }
    }
    .icon-duihao-i {
      color: #2dcb56;
      font-size: 16px;
    }
    .bk-table-footer {
      padding: 0 15px;
      background: #fff;
    }
  }
}
.blue-background-class {
  background: red;
}
</style>
