<template>
  <bk-upload
    ref="uploadRef"
    accept=".xlsx,.xls"
    with-credentials
    :limit="1"
    :size="UPLOAD_FILE_MAX_SIZE"
    :multiple="false"
    :custom-request="customRequest"
    @exceed="exceed"
  >
    <template #file="{ file }">
      <div
        :class="['excel-file', { 'excel-file-error': isError }]"
        @mousemove="isHover = true"
        @mouseleave="isHover = false"
      >
        <i class="user-icon icon-excel" />
        <div class="file-text">
          <bk-overflow-title class="text-overflow">
            {{ file.name }}
          </bk-overflow-title>
          <p class="text-overflow file-status">
            <i v-if="!isError" class="user-icon icon-check-line" />
            {{ textTips }}
          </p>
        </div>
        <div class="file-operations">
          <span v-if="!isHover">{{ getSize(file.size) }}</span>
          <i v-else class="user-icon icon-delete" @click="handleUploadRemove(file)" />
        </div>
      </div>
    </template>
    <template #tip>
      <div class="mt-[8px]">
        <span>{{ $t('支持 Excel 文件，文件小于 {0} M，下载', [UPLOAD_FILE_MAX_SIZE]) }}</span>
        <bk-button text theme="primary" @click="handleExportTemplate">
          {{ $t('模版文件') }}
        </bk-button>
      </div>
    </template>
  </bk-upload>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import { UPLOAD_FILE_MAX_SIZE, UPLOAD_FILE_MAX_SIZE_BYTE } from './constants';

import { t } from '@/language/index';

const model = defineModel<File | null>({ default: null });

const emit = defineEmits<{
  exceed: [];
}>();

const uploadRef = ref();
const isHover = ref(false);
const isError = ref(false);
const textTips = ref('');

const customRequest = (data: { file: File }) => {
  if (data.file.size > UPLOAD_FILE_MAX_SIZE_BYTE) {
    isError.value = true;
    textTips.value = t('文件大小超出限制');
    // 超限文件不赋值给 v-model，避免提交时带上超限文件
    model.value = null;
    return;
  }
  isError.value = false;
  textTips.value = t('上传成功');
  model.value = data.file;
};

const exceed = () => {
  emit('exceed');
};

const getSize = (value: number) => `${parseFloat((value / 1024).toFixed(2))}KB`;

const handleUploadRemove = (file: File) => {
  uploadRef.value?.handleRemove(file);
  model.value = null;
  isError.value = false;
};

const handleExportTemplate = () => {
  window.open(`${window.AJAX_BASE_URL}/api/v3/web/data-sources/operations/download_template/`);
};
</script>

<style lang="less" scoped>
.excel-file {
  display: flex;
  padding: 10px;
  overflow: hidden;
  font-size: 12px;
  align-items: center;
  width: 100%;

  .icon-excel {
    margin-right: 14px;
    font-size: 26px;
    color: #2DCB56;
  }

  .file-text {
    flex: 1;
    overflow: hidden;
  }

  .file-status {
    color: #2DCB56;
  }

  .file-operations {
    .icon-delete {
      margin-left: 12px;
      font-size: 16px;
      cursor: pointer;
    }
  }
}

.excel-file-error {
  background: rgb(254 221 220 / 40%);

  .file-status {
    color: #EA3636;
  }
}
</style>
