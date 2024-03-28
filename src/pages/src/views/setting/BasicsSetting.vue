<template>
  <div class="basics-setting-wrapper">
    <div class="mb-[24px]" v-if="isEdit">
      <bk-form
        ref="formRef"
        form-type="vertical"
        :model="formData"
        :rules="rules">
        <Row title="">
          <div class="flex items-center">
            <div class="w-[560px] mr-[100px]">
              <bk-form-item :label="$t('租户名称')" property="name" required>
                <bk-input v-model="formData.name" :placeholder="validate.name.message" />
              </bk-form-item>
              <bk-form-item :label="$t('租户ID')" property="id" required>
                <bk-input v-model="formData.id" />
              </bk-form-item>
            </div>
            <bk-form-item :label="$t('租户logo')">
              <bk-upload
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
            </bk-form-item>
          </div>
          <bk-form-item :label="$t('租户名')" required>
            <bk-radio-group
              v-model="formData.tenantName"
            >
              <bk-radio-button class="min-w-[100px]" :label="true">显示</bk-radio-button>
              <bk-radio-button class="min-w-[100px]" :label="false">隐藏</bk-radio-button>
            </bk-radio-group>
          </bk-form-item>
          <bk-form-item :label="$t('用户数量')" required>
            <bk-radio-group
              v-model="formData.users"
            >
              <bk-radio-button class="min-w-[100px]" :label="true">显示</bk-radio-button>
              <bk-radio-button class="min-w-[100px]" :label="false">隐藏</bk-radio-button>
            </bk-radio-group>
          </bk-form-item>
        </Row>
      </bk-form>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        theme="primary"
        @click="save"
      >
        {{ $t('保存') }}
      </bk-button>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        @click="isEdit = false"
      >
        {{ $t('取消') }}
      </bk-button>
    </div>
    <div v-else>
      <Row title="">
        <div class="flex items-top justify-between">
          <div>
            <LabelContent :label="$t('租户名称')">{{ formData.name }}</LabelContent>
            <LabelContent :label="$t('租户ID')">{{ formData.id }}</LabelContent>
            <LabelContent :label="$t('租户名')">{{ formData.tenantName ? $t('显示') : $t('隐藏') }}</LabelContent>
            <LabelContent :label="$t('用户数量')">{{ formData.users ? $t('显示') : $t('隐藏') }}</LabelContent>
          </div>
          <LabelContent class="tenant-logo" :label="$t('租户logo')">
            <img v-if="formData.logo" class="user-logo" :src="formData.logo" alt="">
            <i class="user-icon icon-yonghu" />
          </LabelContent>
          <bk-button
            class="min-w-[64px]"
            outline
            theme="primary"
            @click="isEdit = true"
          >
            {{ $t('编辑') }}
          </bk-button>
        </div>
      </Row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, reactive, ref } from 'vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import Row from '@/components/layouts/row.vue';
import { useValidate } from '@/hooks';
import { t } from '@/language/index';
import { useMainViewStore } from '@/store';
import { getBase64 } from '@/utils';

const validate = useValidate();

const store = useMainViewStore();
store.customBreadcrumbs = false;

const formData = reactive({
  name: '',
  id: '',
  tenantName: true,
  users: true,
  logo: '',
});

const rules = {
  name: [validate.required, validate.name],
  id: [validate.required],
};

const isEdit = ref(false);

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

const handleChange = () => {
  window.changeInput = true;
};
</script>

<style lang="less" scoped>
.basics-setting-wrapper {
  padding: 24px;

  ::v-deep .tenant-logo {
    .label-value {
      margin-top: 18px;
    }
  }

  .icon-yonghu {
    padding: 16px;
    font-size: 40px;
    color: #DCDEE5;
    background: #FAFBFD;
    border: 1px dashed #C4C6CC;
    border-radius: 2px;
  }
}
</style>
