<template>
  <div class="edit-user-wrapper user-scroll-y">
    <bk-form
      ref="formRef"
      class="add-user-form"
      form-type="vertical"
      :model="formData"
      :rules="rules"
    >
      <bk-form-item
        style="width: 440px;"
        label="用户名"
        property="username"
        required
      >
        <bk-input
          v-model="formData.username"
          placeholder="数字、下划线(_)、点(.)、减号(-)字符组成，以字母或数字开头"
          :disabled="isEdit"
          @focus="handleChange"
        />
      </bk-form-item>
      <bk-form-item
        style="width: 440px;"
        label="全名"
        property="full_name"
        required
      >
        <bk-input
          v-model="formData.full_name"
          placeholder="全名可随时修改"
          @focus="handleChange"
        />
      </bk-form-item>
      <BkUpload
        theme="picture"
        with-credentials
        :multiple="false"
        :files="files"
        :handle-res-code="handleRes"
        :url="formData.logo"
        :custom-request="customRequest"
        @delete="handleDelete"
      />
      <bk-form-item label="邮箱" property="email" required>
        <bk-input v-model="formData.email" placeholder="请输入" @focus="handleChange" />
      </bk-form-item>
      <bk-form-item label="手机号" required>
        <div class="input-text">
          <input
            type="text"
            ref="telRef"
            :class="['select-text', { 'input-error': telError }]"
            v-model="formData.phone"
            placeholder="请输入"
            @blur="verifyInput"
            @focus="hiddenVerify"
          />
          <p class="error-text" v-show="telError && formData.phone">
            请填写正确的手机号
          </p>
          <p class="error-text" v-show="telError && !formData.phone">
            必填项
          </p>
        </div>
      </bk-form-item>
      <div class="form-item-flex">
        <bk-form-item label="所属组织">
          <bk-select
            v-model="formData.department_ids"
            filterable
            multiple
            :input-search="false"
            :remote-method="searchDepartments"
            :scroll-loading="scrollLoading"
            @scroll-end="departmentsScrollEnd"
            @change="handleChange">
            <bk-option
              v-for="item in state.departments"
              :key="Number(item.id)"
              :value="Number(item.id)"
              :label="item.name" />
          </bk-select>
        </bk-form-item>
        <bk-form-item label="直属上级">
          <bk-select
            v-model="formData.leader_ids"
            filterable
            multiple
            :input-search="false"
            :remote-method="searchLeaders"
            :scroll-loading="scrollLoading"
            @scroll-end="leadersScrollEnd"
            @change="handleChange">
            <bk-option
              v-for="item in state.leaders"
              :key="Number(item.id)"
              :value="Number(item.id)"
              :label="item.username" />
          </bk-select>
        </bk-form-item>
      </div>
      <!-- 一期不做 -->
      <!-- <div class="form-item-flex">
        <bk-form-item label="在职状态" required>
          <bk-radio-group>
            <bk-radio label="在职" />
            <bk-radio label="离职" />
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item label="职务">
          <bk-radio-group>
            <bk-radio label="员工" />
            <bk-radio label="组长" />
          </bk-radio-group>
        </bk-form-item>
      </div>
      <div class="form-item-flex">
        <bk-form-item
          label="账号过期时间"
          property="account_expiration_time"
          required
        >
          <bk-date-picker
            type="datetime"
            v-model="formData.account_expiration_time"
            clearable
          />
        </bk-form-item>
        <bk-form-item
          label="密码过期时间"
          property="password_expiration_time"
          required
        >
          <bk-date-picker
            type="datetime"
            v-model="formData.password_expiration_time"
            clearable
          />
        </bk-form-item>
      </div> -->
    </bk-form>
    <div class="footer">
      <bk-button theme="primary" @click="handleSubmit" :loading="state.isLoading">
        提交
      </bk-button>
      <bk-button @click="() => emit('handleCancelEdit')">
        取消
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import intlTelInput from 'intl-tel-input/build/js/intlTelInput.min';
import telUtils from 'intl-tel-input/build/js/utils';
import { computed, defineEmits, defineProps, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';

import useValidate from '@/hooks/use-validate';
import { getDataSourceDepartments, getDataSourceLeaders, newDataSourceUser, putDataSourceUserDetails } from '@/http/dataSourceFiles';
import { COUNTRY_CODE, getBase64 } from '@/utils';

const props = defineProps({
  type: {
    type: String,
    default: '',
  },
  usersData: {
    type: Object,
    default: () => ({}),
  },
  currentId: {
    type: Number,
  },
  dataSourceId: {
    type: Number,
  },
});
const emit = defineEmits(['updateUsers', 'handleCancelEdit']);

const validate = useValidate();

const formRef = ref();
const formData = reactive({
  ...props.usersData,
});
const state = reactive({
  departments: [],
  leaders: [],
  isLoading: false,
});

watch(() => props.usersData.departments, (val) => {
  if (val) {
    formData.department_ids = props.usersData.departments.map(item => item.id);
    formData.leader_ids = props.usersData.leaders.map(item => item.id);
  }
}, {
  immediate: true,
});

const isEdit = computed(() => props.type === 'edit');
const files = computed(() => {
  const img = [];
  if (formData.logo !== '') {
    img.push({
      url: formData.logo,
    });
    return img;
  }
  return [];
});

const rules = {
  username: [validate.required, validate.userName],
  full_name: [validate.required, validate.name],
  email: [validate.required, validate.email],
  phone: [validate.required, validate.phone],
};
const handleRes = (response: any) => {
  if (response.id) {
    return true;
  }
  return false;
};

const customRequest = (event) => {
  getBase64(event.file).then((res) => {
    formData.logo = res;
  })
    .catch((e) => {
      console.warn(e);
    });
  handleChange();
};

const scrollLoading = ref(false);
const departmentsCount = ref(0);
const leadersCount = ref(0);

const departmentsParams = reactive({
  id: props.dataSourceId,
  name: '',
  page: 1,
  pageSize: 10,
});

const leadersParams = reactive({
  id: props.dataSourceId,
  keyword: '',
  page: 1,
  pageSize: 10,
});

const telRef = ref();
const area = ref('cn');
const iti = ref(null);
const telError = ref(false);

onMounted(async () => {
  if (formData?.phone_country_code) {
    COUNTRY_CODE.forEach((item) => {
      const tel = item.short.toLowerCase();
      if (tel === formData.phone_country_code) {
        area.value = item.tel;
      }
    });
  }
  initIntlTel();
  const departments = await getDataSourceDepartments(departmentsParams);
  const leaders = await getDataSourceLeaders(leadersParams);
  state.departments = departments.data.results;
  departmentsCount.value = departments.data.count;
  state.leaders = leaders.data.results;
  leadersCount.value = leaders.data.count;
});

onBeforeUnmount(() => {
  iti?.value.destroy();
});

const initIntlTel = () => {
  const input = telRef.value;
  try {
    iti.value = intlTelInput(input, {
      allowDropdown: true,
      separateDialCode: true, // 国旗右边显示区号
      formatOnDisplay: false, // 不自动加空格或横线
      placeholderNumberType: 'MOBILE', // 手机号码
      initialCountry: area.value, // 初始国家
      preferredCountries: ['cn', 'us', 'gb'], // 偏好国家 中美英
      utilsScript: telUtils,
    });
  } catch (e) {
    console.warn('手机号国际化初始化失败，默认改为中国', e);
    handleInitError();
  }
  input.addEventListener('countrychange', () => {
    const countryData = iti.value.getSelectedCountryData(); // iso2(eg: cn) dialCode(eg: 86)
    area.value = countryData.iso2;
    formData.phone_country_code = `+${countryData.dialCode}`;
  });
};

const handleInitError = () => {
  const input = telRef.value;
  area.value = 'cn';
  iti.value = intlTelInput(input, {
    allowDropdown: true,
    separateDialCode: true, // 国旗右边显示区号
    formatOnDisplay: false, // 不自动加空格或横线
    placeholderNumberType: 'MOBILE', // 手机号码
    initialCountry: 'cn', // 初始国家
    preferredCountries: ['cn', 'us', 'gb'], // 偏好国家 中美英
    utilsScript: telUtils,
  });
};

const verifyInput = () => {
  if (formData.phone === '') {
    return telError.value = true;
  }
  const validation = area.value === 'cn'
    ? /^1[3-9]\d{9}$/.test(formData.phone)
    : iti.value.isValidNumber();
  !validation && (telError.value = true);
};

const hiddenVerify = () => {
  telError.value = false;
  window.changeInput = true;
};

const departmentsScrollEnd = () => {
  if (departmentsParams.name || departmentsCount.value <= (departmentsParams.page * 10)) return;
  scrollLoading.value = true;
  departmentsParams.page += 1;
  getDataSourceDepartments(departmentsParams).then((res) => {
    state.departments.push(...res.data.results.filter(item => item));
    scrollLoading.value = false;
  })
    .catch((e) => {
      console.warn(e);
      scrollLoading.value = false;
    });
};

const leadersScrollEnd = () => {
  if (leadersParams.keyword || leadersCount.value <= (leadersParams.page * 10)) return;
  scrollLoading.value = true;
  leadersParams.page += 1;
  getDataSourceLeaders(leadersParams).then((res) => {
    state.leaders.push(...res.data.results.filter(item => item));
    scrollLoading.value = false;
  })
    .catch((e) => {
      console.warn(e);
      scrollLoading.value = false;
    });
};

const handleDelete = () => {
  formData.logo = '';
  handleChange();
};

const handleSubmit = async () => {
  await formRef.value.validate();
  state.isLoading = true;
  const data = { ...formData };
  if (!data.logo) delete data.logo;
  let text = '';
  if (props.type === 'edit') {
    data.id = props.currentId;
    text = '用户更新成功';
    await putDataSourceUserDetails(data);
  } else {
    data.id = props.dataSourceId;
    text = '用户创建成功';
    await newDataSourceUser(data);
  }
  emit('updateUsers', '', text);
  state.isLoading = false;
  window.changeInput = false;
};

const searchDepartments = async (value: string) => {
  departmentsParams.name = value;
  departmentsParams.page = 1;
  const departments = await getDataSourceDepartments(departmentsParams);
  state.departments = departments.data.results;
};

const searchLeaders = async (value: string) => {
  leadersParams.keyword = value;
  leadersParams.page = 1;
  const leaders = await getDataSourceLeaders(leadersParams);
  state.leaders = leaders.data.results;
};

const handleChange = () => {
  window.changeInput = true;
};
</script>

<style lang="less">
@import url("@/css/intlTelInput.less");

.iti.iti--allow-dropdown {
  width: 100%;
}
</style>

<style lang="less" scoped>
.edit-user-wrapper {
  position: relative;
  height: calc(100vh - 100px);

  .add-user-form {
    position: relative;
    padding: 28px 40px;

    .bk-upload {
      position: absolute;
      top: 54px;
      right: 32px;
    }

    .form-item-flex {
      display: flex;
      justify-content: space-between;

      .bk-form-item {
        width: 268px;
      }
    }
  }

  .footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    height: 48px;
    padding: 0 24px;
    line-height: 48px;
    background: #FAFBFD;
    box-shadow: 0 -1px 0 0 #DCDEE5;

    .bk-button {
      width: 88px;
      margin-right: 8px;
    }
  }
}

.input-text {
  position: relative;
}

input::placeholder {
  color: #c4c6cc;
}

.select-text {
  width: 100%;
  height: 32px;
  line-height: 32px;
  color: #63656e;
  border: 1px solid #c4c6cc;
  border-radius: 2px;
  outline: none;
  resize: none;
}

.error-text {
  margin: 2px 0 0;
  font-size: 12px;
  line-height: 18px;
  color: #ea3636;
}

.input-error {
  border: 1px solid #ff5656;
}
</style>
