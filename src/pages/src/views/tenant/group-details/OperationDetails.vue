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
              <bk-input v-model="formData.name" @focus="handleChange" />
            </bk-form-item>
            <bk-form-item label="公司ID" property="id" required>
              <bk-input v-model="formData.id" :disabled="isEdit" @focus="handleChange" />
            </bk-form-item>
            <bk-form-item label="人员数量">
              <bk-radio-group v-model="formData.feature_flags.user_number_visible" @change="handleChange">
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
        <bk-input
          type="search"
          placeholder="搜索用户名"
          v-model="state.username"
          clearable
          @enter="handleEnter"
          @clear="handleClear" />
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
                @handleEmpty="handleClear" />
            </template>
          </bk-table>
        </bk-form>
      </div>
      <!-- <div class="operation-card" v-if="!isEdit">
        <div class="operation-content-title">管理员初始密码</div>
        <bk-form
          class="operation-content-form"
          ref="passwordRef"
          :model="formData.password_settings"
          :rules="rulesPasswordInfo"
        >
          <bk-form-item
            class="item-style"
            label="密码生成"
            required
            property="init_password"
          >
            <bk-radio-group v-model="formData.password_settings.init_password_method">
              <bk-radio label="random_password" :disabled="true">随机</bk-radio>
              <bk-radio label="fixed_password">固定</bk-radio>
              <bk-input
                style="margin-left: 24px; width: 240px;"
                v-if="formData.password_settings.init_password_method === 'fixed_password'"
                type="password"
                v-model="formData.password_settings.init_password"
              />
            </bk-radio-group>
          </bk-form-item>
        </bk-form>
      </div> -->
    </div>
    <div class="footer">
      <bk-button theme="primary" @click="handleSubmit">
        提交
      </bk-button>
      <bk-button @click="() => $emit('handleCancelEdit')">
        取消
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="tsx">
import { ref, reactive, computed, nextTick } from "vue";
import { createTenants, putTenants, getTenantUsersList } from "@/http/tenantsFiles";
import { getBase64 } from "@/utils";
import Empty from "@/components/Empty.vue";
import MemberSelector from "./MemberSelector.vue";
import useValidate from "@/hooks/use-validate";

interface TableItem {
  username: string;
  full_name: string;
  email: string;
  phone: string;
  phone_country_code: string,
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
  type: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(['updateTenantsList']);

const validate = useValidate();

const basicRef = ref();
const userRef = ref();
const passwordRef = ref();
const formData = reactive({
  ...props.tenantsData
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
  name: [validate.required, validate.name],
  id: [validate.required, validate.id],
};

const rulesUserInfo = {
  username: [validate.required, validate.userName],
  full_name: [validate.required, validate.name],
  email: [validate.required, validate.email],
  phone: [validate.required, validate.phone],
};

const rulesPasswordInfo = {
  init_password: [validate.required],
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
const isEdit = computed(() => props.type === "edit");

const handleRes = (response: any) => {
  if (response.id) {
    return true;
  }
  return false;
};
const customRequest = (event) => {
  getBase64(event.file).then((res) => {
    formData.logo = res;
  }).catch((e) => {
    console.warn(e);
  });
  handleChange();
}

const handleDelete = () => {
  formData.logo = "";
  handleChange();
};

const fieldItemFn = (row: any) => {
  const { column, index, data } = row;
  return (
    <bk-form-item
      error-display-type="tooltips"
      property={`managers.${index}.${column.field}`}
      rules={rulesUserInfo[column.field]}
    >
      {
        (props.type === 'edit' && !data.id)
          ? column.field === 'username'
            ? <MemberSelector
                v-model={formData.managers[index][column.field]}
                state={state}
                params={params}
                onSelectList={selectList}
                onScrollChange={scrollChange}
                onSearchUserList={fetchUserList} />
            : <bk-input v-model={formData.managers[index][column.field]} disabled={column.field !== 'username'} />
          : <bk-input v-model={formData.managers[index][column.field]} disabled={data.id} onFocus={handleChange} />
      }
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
            onClick={handleItemChange.bind(this, index, 'add')}
          >
            <i class="user-icon icon-plus-fill" />
          </bk-button>
          <bk-button
            text
            disabled={formData.managers.length === 1}
            onClick={handleItemChange.bind(this, index, 'remove')}
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

function handleItemChange(index: number, action: 'add' | 'remove') {
  if(action === 'add') {
    formData.managers.splice(index + 1, 0, getTableItem());
  } else if (action === 'remove') {
    formData.managers.splice(index, 1);
  }

  window.changeInput = true;
  fetchUserList("");
}
// 校验表单
async function handleSubmit() {
  const validationPromises = [
    basicRef.value.validate(),
    userRef.value.validate(),
  ];

  await Promise.all(validationPromises);

  props.type === "add" ? createTenantsFn() : putTenantsFn();
}

// 新建租户
function createTenantsFn() {
  const data = { ...formData };
  if (!data.logo) delete data.logo;

  createTenants(data).then(() => emit('updateTenantsList'));
}
// 更新租户
function putTenantsFn() {
  const manager_ids = formData.managers.map(item => item.id);
  const params = {
    name: formData.name,
    logo: formData.logo,
    feature_flags: {
      user_number_visible: formData.feature_flags.user_number_visible,
    },
    manager_ids,
  };

  if (!params.logo) delete params.logo;

  putTenants(formData.id, params).then(() => emit('updateTenantsList'));
}

// 搜索管理员
const handleEnter = (value: string) => {
  formData.managers = props.tenantsData.managers.filter(item => item.username.includes(value));
  state.isEmptySearch = !formData.managers.length;
}
// 清除搜索管理员
const handleClear = () => {
  state.username = "";
  formData.managers = [...props.tenantsData.managers];
}
// 获取管理员列表
const fetchUserList = (value: string) => {
  params.keyword = value;
  if (params.tenant_id) {
    getTenantUsersList(params).then((res) => {
      const list = formData.managers.map((item) => item.username);
      state.count = res.data.count;
      state.list = res.data.results.filter(
        (item) => !list.includes(item.username)
      );
    });
  }
}

const selectList = (list) => {
  formData.managers = formData.managers.filter(item => item.id);
  nextTick(() => {
    const managers = list && list.length ? list : [{
      username: "",
      full_name: "",
      email: "",
      phone: "",
      phone_country_code: "86",
    }];

    formData.managers.push(...managers);
  });
}

const scrollChange = () => {
  params.page_size += 10;
  getTenantUsersList(params).then((res) => {
    const list = formData.managers.map((item) => item.username);
    state.count = res.data.count;
    state.list = res.data.results.filter(
      (item) => !list.includes(item.username)
    );
  });
}

const handleChange = () => {
  window.changeInput = true;
}
</script>

<style lang="less" scoped>
@import url("@/css/tenantEditStyle.less");
</style>
