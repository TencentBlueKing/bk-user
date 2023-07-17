<template>
  <ul class="operation-content">
    <bk-form
      ref="formRef"
      :model="formData"
      :rules="rules"
    >
      <li>
        <div class="operation-content-title">基本信息</div>
        <div class="operation-content-info">
          <div
            class="operation-content-form"
          >
            <bk-form-item label="公司名称" property="name" required>
              <bk-input v-model="formData.name" placeholder="请输入" clearable />
            </bk-form-item>
            <bk-form-item label="公司ID" property="id" required>
              <bk-input v-model="formData.id" placeholder="请输入" clearable />
            </bk-form-item>
            <bk-form-item label="人员数量">
              <bk-radio-group v-model="formData.isShow">
                <bk-radio :label="true">显示</bk-radio>
                <bk-radio :label="false">隐藏</bk-radio>
              </bk-radio-group>
            </bk-form-item>
          </div>
          <BkUpload
            theme="picture"
            with-credentials
            :files="files"
            :handle-res-code="handleRes"
            :url="'https://jsonplaceholder.typicode.com/posts/'"
          />
        </div>
      </li>
      <li>
        <div class="operation-content-title">管理员</div>
        <bk-input type="search" placeholder="搜索用户名" />
        <bk-table
          class="operation-content-table"
          :border="['col', 'outer']"
          :data="formData.userData"
          :columns="columns"
        />
      </li>
      <li>
        <div class="operation-content-title">管理员初始密码</div>
        <bk-form-item label="密码生成" required>
          <bk-radio-group v-model="formData.initPassword.mode">
            <bk-radio label="random" :disabled="true">随机</bk-radio>
            <bk-radio label="custom">固定</bk-radio>
            <bk-input
              style="margin-left: 24px; width: 240px;"
              v-if="formData.initPassword.mode === 'custom'"
              type="password"
              v-model="formData.initPassword.password" />
          </bk-radio-group>
        </bk-form-item>
      </li>
    </bk-form>
  </ul>
</template>

<script setup lang="tsx">
import { ref, computed, reactive } from "vue";

interface TableItem {
  username: string;
  display_name: string;
  email: string;
  telephone: number | string;
}
interface TableColumnData {
  index: number;
  data: TableItem;
}

const props = defineProps({
    basicInfo: {
    type: Object,
    default: {},
  },
  userData: {
    type: Array,
    default: [],
  },
  initPassword: {
    type: Object,
    default: {},
  },
});

const formRef = ref("");
const formData = reactive({
  name: props.basicInfo.name,
  id: props.basicInfo.id,
  isShow: props.basicInfo.isShow,
  userData: [...props.userData],
  initPassword: props.initPassword,
});

const rules = {
  name: [
    {
      required: true,
      message: "必填项",
      trigger: "blur",
    },
  ],
  id: [
    {
      required: true,
      message: "必填项",
      trigger: "blur",
    },
  ],
};
const files: any = [];

const handleRes = (response: any) => {
  if (response.id) {
    return true;
  }
  return false;
};

const columns = [
  {
    label: "用户名",
    field: "username",
    render: ({ data, index }: TableColumnData) => fieldItemFn(data.username, index),
  },
  {
    label: "全名",
    field: "display_name",
    render: ({ data, index }: TableColumnData) => fieldItemFn(data.display_name, index),
  },
  {
    label: "邮箱",
    field: "email",
    render: ({ data, index }: TableColumnData) => fieldItemFn(data.email, index),
  },
  {
    label: "手机号",
    field: "telephone",
    render: ({ data, index }: TableColumnData) => fieldItemFn(data.telephone, index),
  },
  {
    label: "操作",
    field: "",
    render: ({ data, index }: TableColumnData) => {
      return (
        <div style="font-size: 16px;">
          <bk-button
            style="margin: 0 15px;"
            text
            onClick={handleAddItem.bind(this, index)}
          >
            <i class="user-icon icon-plus-fill" />
          </bk-button>
          <bk-button
            text
            disabled={formData.userData.length === 1}
            onClick={handleRemoveItem.bind(this, index)}
          >
            <i class="user-icon icon-minus-fill" />
          </bk-button>
        </div>
      );
    },
  },
];

const fieldItemFn = (type: string | number, index: number) => {
  return <bk-form-item
    error-display-type="tooltips"
    property={index[type]}
  >
    <bk-input v-model={type} placeholder="请输入" />
  </bk-form-item>
};

/**
 * 获取表格数据
 */
function getTableItem(): TableItem {
  return {
    username: "",
    display_name: "",
    email: "",
    telephone: "",
  };
}

function handleAddItem(index: number) {
  formData.userData.splice(index + 1, 0, getTableItem());
}

function handleRemoveItem(index: number) {
  formData.userData.splice(index, 1);
}
</script>

<style lang="less" scoped>
.details-content {
  padding: 0 40px;
  li {
    list-style: none;
    padding: 20px 0;
    border-bottom: 1px solid #dcdee5;
    position: relative;
    .details-content-title {
      font-size: 14px;
      color: #63656e;
      font-weight: 700;
      line-height: 40px;
    }
    .details-content-info {
      width: calc(100% - 92px);
      .details-content-item {
        line-height: 40px;
        width: 100%;
        .details-content-key {
          font-size: 14px;
          color: #63656e;
          display: inline-block;
          width: 100px;
          text-align: right;
        }
        .details-content-value {
          font-size: 14px;
          color: #313238;
          display: inline-block;
          width: calc(100% - 100px);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          vertical-align: middle;
        }
      }
    }
    .details-content-img {
      font-size: 50px;
      border: 1px solid #c4c6cc;
      color: #c4c6cc;
      padding: 10px;
      position: absolute;
      top: calc(50% - 25%);
      right: 0;
    }
  }
  li:last-child {
    border-bottom: none;
  }
}
.operation-content {
  padding: 0 24px;
  li {
    list-style: none;
    margin: 16px 0;
    padding: 10px 20px;
    background: #fff;
    box-shadow: 0 2px 4px 0 #1919290d;
    border-radius: 2px;
    .operation-content-title {
      font-size: 14px;
      color: #63656e;
      font-weight: 700;
      line-height: 40px;
    }
    .operation-content-info {
      display: flex;
      justify-content: space-between;
      padding-right: 60px;
      .operation-content-form {
        width: 70%;
      }
    }
    .operation-content-table {
      margin-top: 16px;
      :deep(.bk-table-body) {
        .cell {
          padding: 0 !important;
          .bk-form-item {
            margin-bottom: 0;
            .bk-form-content {
              margin-left: 0 !important;
              .bk-input {
                height: 42px;
                border-color: transparent;
              }
              .bk-input:hover:not(.is-disabled) {
                border-color: #3a84ff;
              }
            }
          }
          .user-icon {
            color: #dcdee5;
            &:hover {
              color: #c4c6cc;
            }
          }
        }
      }
    }
  }
}
.details-content-table {
  margin-top: 16px;
  :deep(.bk-fixed-bottom-border) {
    border-top: none;
  }
}
</style>
