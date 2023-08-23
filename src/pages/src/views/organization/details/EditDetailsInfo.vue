<template>
  <div class="operation-wrapper">
    <div class="operation-content">
      <div class="operation-card">
        <div class="operation-content-title">基本信息</div>
        <div class="operation-content-info">
          <bk-form
            class="operation-content-form"
            ref="basicRef"
            :model="formData"
            :rules="rulesBasicInfo"
          >
            <bk-form-item label="公司名称" property="name" required>
              <bk-input v-model="formData.name" />
            </bk-form-item>
            <bk-form-item label="公司ID" property="id" required>
              <bk-input
                v-model="formData.id"
                disabled
              />
            </bk-form-item>
            <bk-form-item label="人员数量">
              <bk-radio-group
                v-model="formData.feature_flags.user_number_visible"
              >
                <bk-radio-button :label="true">显示</bk-radio-button>
                <bk-radio-button :label="false">隐藏</bk-radio-button>
              </bk-radio-group>
            </bk-form-item>
          </bk-form>
          <bk-upload
            theme="picture"
            with-credentials
            :multiple="false"
            :files="files"
            :handle-res-code="handleRes"
            :url="formData.logo"
            :custom-request="customRequest"
            @delete="handleDelete"
          />
        </div>
      </div>
      <div class="operation-card">
        <div class="operation-content-title">管理员</div>
        <bk-form ref="userRef" :model="formData">
          <bk-table
            class="operation-content-table"
            :border="['col', 'outer']"
            :data="formData.managers"
            :columns="columns"
          >
            <template #empty>
              <Empty
                :is-search-empty="state.isEmptySearch"
                @handleEmpty="handleClear"
              />
            </template>
          </bk-table>
        </bk-form>
      </div>
    </div>
    <div class="footer">
      <bk-button theme="primary" @click="handleSubmit">
        提交
      </bk-button>
      <bk-button @click="() => $emit('handleCancel')">
        取消
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="tsx">
import { ref, reactive, computed } from "vue";
import { emailRegx, telRegx } from "@/common/regex";
import { getBase64 } from "@/utils";
import Empty from "@/components/Empty.vue";
import MemberSelector from "@/views/tenant/group-details/MemberSelector.vue";

interface TableItem {
  username: string;
  full_name: string;
  email: string;
  phone: string;
  phone_country_code: string;
}
interface TableColumnData {
  index: number;
  data: TableItem;
}

const props = defineProps({
  tenantsData: {
    type: Object,
    default: {},
  },
});

const basicRef = ref();
const userRef = ref();
const passwordRef = ref();
const formData = reactive({
  ...props.tenantsData,
});
const state = reactive({
  username: "",
  // 搜索结果为空
  isEmptySearch: false,
  count: 0,
  list: [],
});

const params = reactive({
  tenant_id: props.tenantsData.id,
  keyword: "",
  page: 1,
  page_size: 10,
});

const rulesBasicInfo = {
  name: [
    {
      required: true,
      message: "必填项",
      trigger: "blur",
    },
    {
      validator: (value: string) => value.length <= 32,
      message: "不能多于32个字符",
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

const rulesUserInfo = {
  username: [
    {
      required: true,
      message: "必填项",
      trigger: "blur",
    },
    {
      validator: (value: string) => {
        return value.length <= 32;
      },
      message: "不能多于32个字符",
      trigger: "blur",
    },
  ],
  full_name: [
    {
      required: true,
      message: "必填项",
      trigger: "blur",
    },
    {
      validator: (value: string) => value.length <= 32,
      message: "不能多于32个字符",
      trigger: "blur",
    },
  ],
  email: [
    {
      required: true,
      message: "必填项",
      trigger: "blur",
    },
    {
      validator: (value: string) => emailRegx.rule.test(value),
      message: emailRegx.message,
      trigger: "blur",
    },
  ],
  phone: [
    {
      required: true,
      message: "必填项",
      trigger: "blur",
    },
    {
      validator: (value: string) => telRegx.rule.test(value),
      message: telRegx.message,
      trigger: "blur",
    },
  ],
};

const rulesPasswordInfo = {
  init_password: [
    {
      required: true,
      message: "必填项",
      trigger: "blur",
    },
  ],
};

const files = computed(() => {
  const img = [];
  if (formData.logo !== "") {
    img.push({
      url: formData.logo,
    });
    return img;
  }
  return [];
});

const handleRes = (response: any) => {
  if (response.id) {
    return true;
  }
  return false;
};
const customRequest = (event) => {
  getBase64(event.file)
    .then((res) => {
      formData.logo = res;
    })
    .catch((e) => {
      console.warn(e);
    });
};

const handleDelete = () => {
  formData.logo = "";
};

const fieldItemFn = (row: any) => {
  const { column, index, data } = row;
  return (
    <bk-form-item
      error-display-type="tooltips"
      property={`managers.${index}.${column.field}`}
      rules={rulesUserInfo[column.field]}
    >
      {!data.id ? (
        column.field === "username" ? (
          <MemberSelector
            v-model={formData.managers[index][column.field]}
            state={state}
            params={params}
          />
        ) : (
          <bk-input
            v-model={formData.managers[index][column.field]}
            disabled={column.field !== "username"}
          />
        )
      ) : (
        <bk-input
          v-model={formData.managers[index][column.field]}
          disabled={data.id}
        />
      )}
    </bk-form-item>
  );
};
const columns = [
  {
    label: "用户名",
    field: "username",
    render: fieldItemFn,
  },
  {
    label: "姓名",
    field: "full_name",
    render: fieldItemFn,
  },
  {
    label: "邮箱",
    field: "email",
    render: fieldItemFn,
  },
  {
    label: "手机号",
    field: "phone",
    width: 150,
    render: fieldItemFn,
  },
  {
    label: "操作",
    field: "",
    width: 65,
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
            disabled={formData.managers.length === 1}
            onClick={handleRemoveItem.bind(this, index)}
          >
            <i class="user-icon icon-minus-fill" />
          </bk-button>
        </div>
      );
    },
  },
];

/**
 * 获取表格数据
 */
function getTableItem(): TableItem {
  return {
    username: "",
    full_name: "",
    email: "",
    phone: "",
    phone_country_code: "86",
  };
}

function handleAddItem(index: number) {
  formData.managers.splice(index + 1, 0, getTableItem());
}

function handleRemoveItem(index: number) {
  formData.managers.splice(index, 1);
}
// 校验表单
function handleSubmit() {}
</script>

<style lang="less" scoped>
@import url("@/css/tenantEditStyle.less");
</style>
