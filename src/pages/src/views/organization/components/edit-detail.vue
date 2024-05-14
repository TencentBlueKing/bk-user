<template>
    <div class="operation-wrapper user-scroll-y">
      <bk-form
        class="operation-content"
        ref="formRef"
        form-type="vertical"
        :model="formData"
        :rules="rules">
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
        <bk-form-item :label="$t('全名')" property="full_name" required>
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
              v-model="formData.departments"
              filterable
              multiple
              :input-search="false"
              :remote-method="searchDepartments"
              :scroll-loading="scrollLoading"
              @scroll-end="departmentsScrollEnd"
              @change="handleChange">
              <bk-option
                v-for="item in departmentsList"
                :key="item.id"
                :value="item.id"
                :label="item.name" />
            </bk-select>
          </bk-form-item>
          <bk-form-item :label="$t('直属上级')">
            <bk-select
              v-model="formData.leaders"
              filterable
              multiple
              :input-search="false"
              :remote-method="searchLeaders"
              :scroll-loading="scrollLoading"
              @scroll-end="leadersScrollEnd"
              @change="handleChange">
              <bk-option
                v-for="item in leaderList"
                :key="item.id"
                :value="item.id"
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
  
  <script setup lang="ts">
  import { reactive, ref, onMounted } from 'vue';
  import CustomFields from '@/components/custom-fields/index.vue';
  import PhoneInput from '@/components/phoneInput.vue';
  import { useValidate } from '@/hooks';
  import { newVirtualUsers, putVirtualUsers } from '@/http';
  import {
    optionalDepartmentsList,
    optionalLeaderList,
    updateTenantsUserDetail
  } from '@/http/organizationFiles';
  import { getFields } from '@/http/settingFiles';
  import { t } from '@/language/index';
  
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
  
  const changeCountryCode = (code: string) => {
    formData.phone_country_code = code;
  };
  
  const telError = ref(false);
  
  const changeTelError = (value: boolean) => {
    telError.value = value;
  };
  const searchDepartments = (value: string) => {
    if (value.length > 1) {
        optionalDepartmentsList({keyword: value}).then((res) => {
            departmentsList.value = res.data;
        })
        .catch((e) => {
            console.warn(e);
        });
    }
  };
  const searchLeaders = (value: string) => {
    if (value.length > 1) {
        optionalLeaderList({keyword: value, excluded_user_id: formData.id}).then((res) => {
            leaderList.value = res.data;
        })
        .catch((e) => {
            console.warn(e);
        });
    }
  };
  
  const handleSubmit = async () => {
    try {
      await formRef.value.validate();
      if (telError.value) return;
      isLoading.value = true;
      const { id, logo, status, extras, ...param} = formData;
      const extraData = {};
      extras.map(item => extraData[item.name] = item.value || item.default);
      await updateTenantsUserDetail(id, {...param, ...{extras: extraData}});
      emit('updateUsers', t('更新成功'));
    } finally {
      isLoading.value = false;
    }
  };
  
  const handleChange = () => {
    window.changeInput = true;
  };
  </script>
  
  <style lang="less" scoped>
  .operation-wrapper {
    padding: 28px 40px;
  
    .footer {
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
  </style>
  