<template>
  <div class="operation-wrapper">
    <div class="operation-content">
      <div class="operation-card">
        <div class="operation-content-title">基本信息</div>
        <div class="operation-content-info">
          <bk-form
            class="operation-content-form"
            ref="basicRef"
            form-type="vertical"
            :model="formData"
            :rules="rulesBasicInfo"
          >
            <bk-form-item label="租户名称" property="name" required>
              <bk-input v-model="formData.name" @focus="handleChange" />
            </bk-form-item>
            <bk-form-item label="租户ID" property="id" required>
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
        <bk-form ref="userRef" :model="formData">
          <bk-table
            class="operation-content-table"
            :border="['col', 'outer']"
            :data="formData.managers"
            :columns="columns"
          >
          </bk-table>
        </bk-form>
      </div>
      <div class="operation-card" v-if="!isEdit">
        <div class="operation-content-title">管理员初始密码</div>
        <bk-form
          form-type="vertical"
          :model="formData.password_initial_config"
        >
          <bk-form-item class="form-item-password" label="密码生成" required>
            <bk-radio-group v-model="formData.password_initial_config.generate_method">
              <bk-radio label="random">
                <span v-bk-tooltips="{ content: '所有管理员的密码都随机生成，互不相同' }">随机</span>
              </bk-radio>
              <bk-radio label="fixed">
                <span v-bk-tooltips="{ content: '所有管理员的密码都一致' }">固定</span>
              </bk-radio>
            </bk-radio-group>
            <bk-input
              class="input-password"
              v-if="formData.password_initial_config.generate_method === 'fixed'"
              type="password"
              v-model="formData.password_initial_config.fixed_password"
            >
              <template #prefix>
                <span class="prefix-slot" @click="handleRandomPassword">随机生成</span>
              </template>
            </bk-input>
          </bk-form-item>
          <bk-form-item label="通知方式" required>
            <NotifyEditorTemplate
              :active-methods="formData.password_initial_config.notification.enabled_methods"
              :checkbox-info="NOTIFICATION_METHODS"
              :data-list="formData.password_initial_config.notification.templates"
              :is-template="isPasswordInitial"
              :expiring-email-key="'user_initialize'"
              :expired-email-key="'reset_password'"
              :expiring-sms-key="'user_initialize'"
              :expired-sms-key="'reset_password'"
              :create-account-email="'创建账户邮件'"
              :reset-password-email="'重设密码后的邮件'"
              :create-account-sms="'创建账户短信'"
              :reset-password-sms="'重设密码后的短信'"
              @handleEditorText="handleEditorText">
              <template #label>
                <div class="password-header">
                  <bk-checkbox-group
                    class="checkbox-zh"
                    v-model="formData.password_initial_config.notification.enabled_methods">
                    <bk-checkbox
                      v-for="(item, index) in NOTIFICATION_METHODS" :key="index"
                      :class="['password-tab', item.status ? 'active-tab' : '']"
                      style="margin-left: 5px;"
                      :label="item.value">
                      <span class="checkbox-item" @click="handleClickLabel(item)">{{item.label}}</span>
                    </bk-checkbox>
                  </bk-checkbox-group>
                  <div class="edit-info" @click="passwordInitialTemplate">
                    <span style="font-size:14px">编辑通知模板</span>
                    <AngleUp v-if="isDropdownPasswordInitial" />
                    <AngleDown v-else />
                  </div>
                </div>
              </template>
            </NotifyEditorTemplate>
            <p class="error" v-show="enabledMethodsError">通知方式不能为空</p>
          </bk-form-item>
        </bk-form>
      </div>
    </div>
    <div class="footer">
      <bk-button theme="primary" @click="handleSubmit" :loading="state.isLoading">
        提交
      </bk-button>
      <bk-button @click="() => $emit('handleCancelEdit')">
        取消
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="tsx">
import { AngleDown, AngleUp } from 'bkui-vue/lib/icon';
import { ref, reactive, computed, nextTick, defineProps, defineEmits, watch } from "vue";
import { createTenants, putTenants, getTenantUsersList } from "@/http/tenantsFiles";
import { getBase64, NOTIFICATION_METHODS } from "@/utils";
import MemberSelector from "./MemberSelector.vue";
import useValidate from "@/hooks/use-validate";
import NotifyEditorTemplate from '@/components/notify-editor/NotifyEditorTemplate.vue';
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { randomPasswords } from '@/http/dataSourceFiles';
import PhoneInput from '@/components/phoneInput.vue';

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
const formData = reactive({
  ...props.tenantsData
});
const state = reactive({
  count: 0,
  list: [],
  isLoading: false,
});

const params = reactive({
  tenantId: props.tenantsData.id,
  keyword: "",
  page: 1,
  pageSize: 10,
});

const rulesBasicInfo = {
  name: [validate.required, validate.name],
  id: [validate.required, validate.id],
};

const rulesUserInfo = {
  username: [validate.required, validate.userName],
  full_name: [validate.required, validate.name],
  email: [validate.required, validate.email],
};

const rulesUserName = {
  username: [validate.required],
};

const enabledMethodsError = ref(false);
// 初始密码
const isPasswordInitial = ref(false);
const isDropdownPasswordInitial = ref(false);

watch(() => formData.password_initial_config?.generate_method, (value) => {
  if (value === 'random') {
    formData.password_initial_config.fixed_password = null;
  }
});

watch(() => formData.password_initial_config?.notification?.enabled_methods, (value) => {
  enabledMethodsError.value = !value.length;
});

const handleClickLabel = (item) => {
  NOTIFICATION_METHODS.forEach((element) => {
    element.status = element.value === item.value;
  });
};

const passwordInitialTemplate = () => {
  isPasswordInitial.value = !isPasswordInitial.value;
  isDropdownPasswordInitial.value = !isDropdownPasswordInitial.value;
};

const handleEditorText = (html, text, key, type) => {
  formData.password_initial_config.notification.templates.forEach((item) => {
    if (item.method === type && item.scene === key) {
      item.content = text;
      item.content_html = html;
    }
  });
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

watch(() => props.tenantsData.managers, (value) => {
  if (value.length > 0) {
    formData.managers = value;
  } else {
    formData.managers.splice(1, 0, getTableItem());
    nextTick(() => {
      fetchUserList('');
    });
  }
}, {
  deep: true,
  immediate: true,
})

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
      rules={props.type === 'add' ? rulesUserInfo[column.field] :  rulesUserName[column.field]}
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
            : (
              column.field === 'phone'
                ? <PhoneInput
                    id="phone-id"
                    form-data={formData.managers[index]}
                    disabled={props.type === 'edit'} />
                : <bk-input v-model={formData.managers[index][column.field]} disabled={column.field !== 'username'} />
            )
          : (
            column.field === 'phone'
              ? <PhoneInput
                  id="phone-id"
                  form-data={formData.managers[index]}
                  telError={formData.managers[index].error}
                  disabled={props.type === 'edit'}
                  tooltips={true}
                  onChangeCountryCode={(code: string) => changeCountryCode(code, index)}
                  onChangeTelError={(value: boolean) => changeTelError(value, index)} />
              : <bk-input v-model={formData.managers[index][column.field]} disabled={data.id} onFocus={handleChange} />
          )
      }
    </bk-form-item>
  );
};

const changeCountryCode = (code: string, index: number) => {
  formData.managers[index].phone_country_code = code;
};

const changeTelError = (value: boolean, index: number) => {
  formData.managers[index].error = value;
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
    width: 200,
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
            style="margin: 0 10px;"
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

const phoneError = ref(false);
// 校验表单
async function handleSubmit() {
  if (enabledMethodsError.value) return;

  formData.managers?.forEach((item) => {
    item.error = item.phone === '' || item.error;
    phoneError.value = item.error;
    if (!item.error) {
      delete item.error;
      delete item.disabled;
    };
  });
  
  await Promise.all([basicRef.value.validate(), userRef.value.validate()]);
  if (phoneError.value) return;

  state.isLoading = true;
  props.type === "add" ? createTenantsFn() : putTenantsFn();
}

// 新建租户
function createTenantsFn() {
  const data = { ...formData };
  if (!data.logo) delete data.logo;

  createTenants(data).then(() => {
    emit('updateTenantsList', '租户创建成功');
  }).finally(() => {
    state.isLoading = false;
  });
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

  putTenants(formData.id, params).then(() => {
    emit('updateTenantsList', '租户更新成功');
  }).finally(() => {
    state.isLoading = false;
  });
}
// 获取管理员列表
const fetchUserList = (value: string) => {
  params.keyword = value;
  params.page = 1;
  if (params.tenantId) {
    getTenantUsersList(params).then((res) => {
      const list = formData.managers.map((item) => item.id);
      state.count = res.data.count;
      state.list = res.data.results.map(item => ({
        ...item,
        disabled: list.includes(item.id),
      }));
    });
  }
}

const selectList = (list) => {
  formData.managers = formData.managers.filter(item => item.id);
  if (list?.length) {
    formData.managers.push(...list);
    userRef.value.validate();
  } else {
    nextTick(() => {
      const managers = [{
        username: "",
        full_name: "",
        email: "",
        phone: "",
        phone_country_code: "86",
      }];

      formData.managers.push(...managers);
    });
  }
};

const scrollChange = () => {
  params.page += 1;
  getTenantUsersList(params).then((res) => {
    const list = formData.managers.map((item) => item.id);
    state.count = res.data.count;
    state.list.push(...res.data.results.map(item => ({
      ...item,
      disabled: list.includes(item.id),
    })));
  });
}

const handleChange = () => {
  window.changeInput = true;
}

const handleRandomPassword = async () => {
  try {
    const passwordRes = await randomPasswords();
    formData.password_initial_config.fixed_password = passwordRes.data.password;
    window.changeInput = true;
  } catch (e) {
    console.warn(e);
  }
};
</script>

<style lang="less" scoped>
@import url("@/css/tenantEditStyle.less");
@import url('@/components/notify-editor/NotifyEditor.less');

.form-item-password {
  ::v-deep .bk-form-content {
    display: flex;

    .bk-radio-label span {
      border-bottom: 1px dashed #979ba5;
    }

    .input-password {
      width: 380px;
      margin-left: 24px;
    }
  }
}

.error {
  position: absolute;
  left: 0;
  padding-top: 4px;
  font-size: 12px;
  line-height: 1;
  color: #ea3636;
  text-align: left;
  animation: form-error-appear-animation 0.15s;
}

.prefix-slot {
  display: flex;
  width: 80px;
  color: #63656e;
  cursor: pointer;
  background: #e1ecff;
  align-items: center;
  justify-content: center;
}
</style>
