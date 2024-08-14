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
                <bk-input v-model="formData.id" readonly />
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
                :tip="$t('支持 jpg、png，尺寸不大于 1024px*1024px，不大于 256KB')"
              />
            </bk-form-item>
          </div>
          <bk-form-item :label="$t('租户名')" required>
            <bk-radio-group
              v-model="formData.visible"
            >
              <bk-radio-button class="min-w-[100px]" :label="true">{{ $t('显示') }}</bk-radio-button>
              <bk-radio-button class="min-w-[100px]" :label="false">{{ $t('隐藏') }}</bk-radio-button>
            </bk-radio-group>
          </bk-form-item>
          <bk-form-item :label="$t('用户数量')" required>
            <bk-radio-group
              v-model="formData.user_number_visible"
            >
              <bk-radio-button class="min-w-[100px]" :label="true">{{ $t('显示') }}</bk-radio-button>
              <bk-radio-button class="min-w-[100px]" :label="false">{{ $t('隐藏') }}</bk-radio-button>
            </bk-radio-group>
          </bk-form-item>
        </Row>
      </bk-form>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        theme="primary"
        @click="saveEdit"
        :disabled="isDisabled"
      >
        {{ $t('保存') }}
      </bk-button>
      <bk-button
        class="min-w-[88px] mr-[8px]"
        @click="cancelEdit"
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
            <LabelContent :label="$t('租户名')">{{ formData.visible ? $t('显示') : $t('隐藏') }}</LabelContent>
            <LabelContent :label="$t('用户数量')">{{ formData.user_number_visible ? $t('显示') : $t('隐藏') }}</LabelContent>
          </div>
          <LabelContent class="tenant-logo" :label="$t('租户logo')">
            <img v-if="formData.logo" class="user-logo" :src="formData.logo" alt="">
            <i v-else class="user-icon icon-yonghu" />
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
import { computed, onMounted, ref, watch } from 'vue';

import Row from '@/components/layouts/ItemRow.vue';
import LabelContent from '@/components/layouts/LabelContent.vue';
import { useValidate } from '@/hooks';
import { getTenantInfo, PutTenantInfo } from '@/http';
import { t } from '@/language/index';
import { useMainViewStore } from '@/store';
import { getBase64 } from '@/utils';

const validate = useValidate();

const store = useMainViewStore();
store.customBreadcrumbs = false;

const formData = ref({
  id: '',
  name: '',
  logo: '',
  visible: true,
  user_number_visible: true,
});

const rules = {
  name: [validate.required, validate.name],
  id: [validate.required],
};

const isEdit = ref(false);

watch(() => isEdit.value, (val) => {
  window.changeInput = val;
}, {
  deep: true,
});

onMounted(() => {
  initTenantInfo();
});

let originalData = {};
const isDisabled = ref(true);
const initTenantInfo = async () => {
  const res = await getTenantInfo();
  originalData = JSON.stringify(res.data);
  formData.value = res.data;
};

watch(formData, () => {
  isDisabled.value = originalData  === JSON.stringify(formData.value);
}, { deep: true });
// 上传头像
const files = computed(() => {
  const img = [];
  if (formData.value.logo !== '') {
    img.push({
      url: formData.value.logo,
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
    formData.value.logo = res;
  })
    .catch((e) => {
      console.warn(e);
    });
};

const handleDelete = () => {
  formData.value.logo = '';
};

const handleError = (file) => {
  if (file.size > (2 * 1024 * 1024)) {
    Message({ theme: 'error', message: t('图片大小超出限制，请重新上传') });
  }
};

const saveEdit = () => {
  const { id, ...params } = formData.value;
  PutTenantInfo(params).then(() => {
    isEdit.value = false;
    Message({ theme: 'success', message: t('保存成功') });
    initTenantInfo();
  });
};

const cancelEdit = () => {
  isEdit.value = false;
  initTenantInfo();
};
</script>

<style lang="less" scoped>
.basics-setting-wrapper {
  padding: 24px;

  .tenant-logo {
    position: relative;
  }

  .user-logo {
    position: absolute;
    top: 10px;
    width: 72px;
    height: 72px;
    border: 1px dashed #C4C6CC;
    border-radius: 2px;
  }

  .icon-yonghu {
    position: absolute;
    top: 10px;
    padding: 16px;
    font-size: 40px;
    color: #DCDEE5;
    background: #FAFBFD;
    border: 1px dashed #C4C6CC;
    border-radius: 2px;
  }
}

:deep(.bk-upload__tip) {
  color: #999
}
</style>
