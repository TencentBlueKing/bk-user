<template>
  <div class="operation-wrapper">
    <bk-form
      class="operation-content user-scroll-y"
      ref="formRef"
      form-type="vertical"
      :model="formData"
      :rules="rules">
      <div class="flex justify-between">
        <div class="w-[424px]">
          <bk-form-item v-if="formData.id" :label="$t('用户ID')" :min-width="280">
            <bk-input
              v-model="formData.id"
              disabled
            />
          </bk-form-item>
          <bk-form-item :label="$t('用户名')" property="username" required>
            <bk-input
              v-model="formData.username"
              :placeholder="validate.userName.message"
              :disabled="formData.id"
              @focus="handleChange"
            />
          </bk-form-item>
        </div>
        <bk-upload
          class="mt-[26px]"
          theme="picture"
          with-credentials
          :multiple="false"
          :files="files"
          :handle-res-code="handleRes"
          :url="formData.logo"
          :custom-request="customRequest"
          :size="2"
          @delete="handleDelete"
          @error="handleError"
          :tip="$t('支持 jpg、png，尺寸不大于 1024px*1024px，不大于 256KB')"
        />
      </div>
      <bk-form-item :label="$t('姓名')" property="full_name" required>
        <bk-input
          v-model="formData.full_name"
          :placeholder="validate.name.message"
          @focus="handleChange"
        />
      </bk-form-item>
      <bk-form-item :label="$t('邮箱')" property="email">
        <bk-input
          v-model="formData.email"
          @focus="handleChange"
        />
      </bk-form-item>
      <bk-form-item :label="$t('手机号')">
        <PhoneInput
          :form-data="formData"
          :tel-error="telError"
          :required="false"
          @change-country-code="changeCountryCode"
          @change-tel-error="changeTelError" />
      </bk-form-item>
      <div class="form-item-flex">
        <bk-form-item :label="$t('所属组织')">
          <bk-select
            v-model="formData.department_ids"
            filterable
            multiple
            :input-search="false"
            multiple-mode="tag"
            collapse-tags
            :list="departmentsList"
            id-key="id"
            display-key="organization_path"
            :remote-method="searchDepartments"
            :scroll-loading="scrollLoading"
            @scroll-end="departmentsScrollEnd"
            @change="handleChange">
          </bk-select>
        </bk-form-item>
        <bk-form-item :label="$t('直属上级')">
          <bk-select
            v-model="formData.leader_ids"
            filterable
            multiple
            :input-search="false"
            multiple-mode="tag"
            collapse-tags
            id-key="id"
            :remote-method="searchLeaders"
            :scroll-loading="scrollLoading"
            @scroll-end="leadersScrollEnd"
            @change="handleChange">
            <bk-option
              v-for="item in leaderList"
              :key="item.id"
              :value="item.id"
              :name="`${item.username}(${item.full_name})`"
              :label="`${item.username}(${item.full_name})`" />
          </bk-select>
        </bk-form-item>
      </div>
      <div class="form-item-flex">
        <bk-form-item :label="$t('账号过期时间')">
          <bk-date-picker
            v-model="formData.account_expired_at"
            :placeholder="$t('选择日期时间')"
            type="datetime"
            format="yyyy-MM-dd HH:mm:ss"
            :disabled-date="disabledDate">
          </bk-date-picker>
        </bk-form-item>
      </div>
      <CustomFields :extras="formData.extras" :rules="rules" />
    </bk-form>
    <div class="footer">
      <bk-button theme="primary" @click="handleSubmit" :loading="isLoading" :disabled="isDisabled">
        {{ $t('保存') }}
      </bk-button>
      <bk-button @click="emit('handleCancelEdit')">
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="tsx">
import { Message } from 'bkui-vue';
import { computed,  onMounted, reactive, ref, watch } from 'vue';

import CustomFields from '@/components/custom-fields/index.vue';
import PhoneInput from '@/components/phoneInput.vue';
import { useValidate } from '@/hooks';
import {
  optionalDepartmentsList,
  optionalLeaderList,
  updateTenantsUserDetail,
} from '@/http/organizationFiles';
import { t } from '@/language/index';
import { getBase64 } from '@/utils';

const props = defineProps({
  detailsInfo: {
    type: Object,
    default: {},
  },
});

const emit = defineEmits(['handleCancelEdit', 'updateUsers']);

const validate = useValidate();
const formRef = ref();
const departmentsList = ref([]);
const leaderList = ref([]);

const formData = reactive({
  ...props.detailsInfo,
});
const originalData = { ...props.detailsInfo,  extras: JSON.parse(JSON.stringify(props.detailsInfo.extras)) };
const isDisabled = ref(true);
const rules = ref({
  username: [validate.required, validate.userName],
  full_name: [validate.required, validate.name],
  email: [validate.emailNotRequired],
});

const isLoading = ref(false);
const disabledDate = date => date.valueOf() < Date.now();

watch(formData, (val) => {
  val.extras.forEach((item) => {
    val[item.name] = item.value;
    if (item.required) {
      rules.value[item.name] = [validate.required];
    }
  });
  isDisabled.value = originalData.id ? JSON.stringify(originalData) === JSON.stringify(formData) : false;
  window.changeInput = !isDisabled.value;
}, { deep: true, immediate: true });

// 上传头像
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
const handleDelete = () => {
  formData.logo = '';
  handleChange();
};
const handleError = (file) => {
  if (file.size > (2 * 1024 * 1024)) {
    Message({ theme: 'error', message: t('图片大小超出限制，请重新上传') });
  }
};

onMounted(() => {
  getOptionalDepartmentsList();
  getOptionalLeaderList();
});

const changeCountryCode = (code: string) => {
  formData.phone_country_code = code;
};

const telError = ref(false);

const changeTelError = (value: boolean) => {
  telError.value = value;
};
const getOptionalDepartmentsList = (value = '') => {
  optionalDepartmentsList({ keyword: value }).then((res) => {
    departmentsList.value = res.data;
  })
    .catch((e) => {
      console.warn(e);
    });
};
const getOptionalLeaderList = (value = '') => {
  optionalLeaderList({ keyword: value, excluded_user_id: formData.id }).then((res) => {
    leaderList.value = res.data;
  })
    .catch((e) => {
      console.warn(e);
    });
};
const searchDepartments = (value: string) => {
  getOptionalDepartmentsList(value);
};
const searchLeaders = (value: string) => {
  getOptionalLeaderList(value);
};

const handleSubmit = async () => {
  try {
    await formRef.value.validate().then(async () => {
      if (telError.value) return;
      isLoading.value = true;
      const { id, status, extras, departments, leaders, ...param } = formData;
      const extraData = {};
      extras.map(item => extraData[item.name] = item.value || item.default);
      await updateTenantsUserDetail(id, { ...param, ...{ extras: extraData } });
      emit('updateUsers', t('更新成功'));
    })
      .catch((err) => {
        console.log(err, 'err');
      });
  } finally {
    isLoading.value = false;
  }
};

const handleChange = () => {
  window.changeInput = true;
};
</script>
  <style lang="less">
  .tag-item-tpl {
    height: 32px;
    padding: 0 8px;
    line-height: 32px;
    color: #63656e;
  }
  </style>
  <style lang="less" scoped>
.operation-content {
  max-height: calc(100vh - 125px);
  padding: 28px 40px;
}

.operation-wrapper {
  .footer {
    padding-left: 40px;
    margin-top: 32px;

    .bk-button {
      width: 88px;
      margin-right: 8px;
    }
  }
}

.form-item-flex {
  display: flex;
  justify-content: space-between;

  .bk-form-item {
    width: 268px;
  }
}

::v-deep .bk-upload__tip {
  width: 0;
  color: #999
}
  </style>
