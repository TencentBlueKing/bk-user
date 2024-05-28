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
              idKey="id"
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
              idKey="id"
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
        <CustomFields :extras="formData.extras" :rules="rules" />
      </bk-form>
      <div class="footer">
        <bk-button theme="primary" @click="handleSubmit" :loading="isLoading">
          {{ $t('保存') }}
        </bk-button>
        <bk-button @click="emit('handleCancelEdit')">
          {{ $t('取消') }}
        </bk-button>
      </div>
    </div>
  </template>
  
  <script setup lang="tsx">
  import { reactive, ref, onMounted, computed } from 'vue';
  import CustomFields from '@/components/custom-fields/index.vue';
  import PhoneInput from '@/components/phoneInput.vue';
  import { useValidate } from '@/hooks';
  import { newVirtualUsers, putVirtualUsers } from '@/http';
  import { Message } from 'bkui-vue';
  import {
    optionalDepartmentsList,
    optionalLeaderList,
    updateTenantsUserDetail
  } from '@/http/organizationFiles';
  import { getFields } from '@/http/settingFiles';
  import { t } from '@/language/index';
  import { getBase64 } from '@/utils';
  
  const emit = defineEmits(['handleCancelEdit', 'updateUsers']);
  
  const props = defineProps({
    detailsInfo: {
      type: Object,
      default: {},
    },
  });
  const validate = useValidate();
  const formRef = ref();
  const departmentsList = ref([]);
  const leaderList = ref([]);

  const formData = reactive({
    ...props.detailsInfo
  });
  
  const rules = {
    username: [validate.required, validate.userName],
    full_name: [validate.required, validate.name],
    email: [validate.emailNotRequired],
  };
  
  const isLoading = ref(false);
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
  })
  
  const changeCountryCode = (code: string) => {
    formData.phone_country_code = code;
  };
  
  const telError = ref(false);
  
  const changeTelError = (value: boolean) => {
    telError.value = value;
  };
  const getOptionalDepartmentsList = (value = '') => {
    optionalDepartmentsList({keyword: value}).then((res) => {
        departmentsList.value = res.data;
    })
    .catch((e) => {
        console.warn(e);
    });
  }
  const getOptionalLeaderList = (value = '') => {
    optionalLeaderList({keyword: value, excluded_user_id: formData.id}).then((res) => {
        leaderList.value = res.data;
    }).catch((e) => {
        console.warn(e);
    });
  }
  const searchDepartments = (value: string) => {
    getOptionalDepartmentsList(value);
  };
  const searchLeaders = (value: string) => {
    getOptionalLeaderList(value);
  };
  
  const handleSubmit = async () => {
    try {
      await formRef.value.validate();
      if (telError.value) return;
      isLoading.value = true;
      const { id, status, extras, departments, leaders, ...param} = formData;
      const extraData = {};
      extras.map(item => extraData[item.name] = item.value || item.default);
      await updateTenantsUserDetail(id, {...param, ...{extras: extraData}});
      emit('updateUsers', t('更新成功'));
    } finally {
      isLoading.value = false;
    }
  };

  const selectTpl = (d) => {
    return (<li class="tag-item-tpl">{`${d.username}(${d.full_name})`}</li>)
  }
  
  const handleChange = () => {
    window.changeInput = true;
  };
  </script>
  <style lang="less">
  .tag-item-tpl {
    height: 32px;
    line-height: 32px;
    padding: 0 8px;
    color: #63656e;
  }
  </style>
  <style lang="less" scoped>
  .operation-content {
    padding: 28px 40px;
    max-height: calc(100vh - 125px);
  }
  .operation-wrapper {
    .footer {
      margin-top: 32px;
      padding-left: 40px;
  
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
  </style>
  