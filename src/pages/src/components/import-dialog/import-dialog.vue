<template>
  <bk-dialog
      :is-show="isShow"
      :title="importConfig.title"
      :quick-close="false"
      :width="640"
      @closed="closed"
    >
      <bk-upload
        ref="uploadRef"
        accept=".xlsx,.xls"
        with-credentials
        :limit="1"
        :size="10"
        :multiple="false"
        :custom-request="customRequest"
        @exceed="exceed">
        <template #file="{ file }">
          <div
            :class="['excel-file', { 'excel-file-error': isError }]"
            @mousemove="isHover = true"
            @mouseleave="isHover = false">
            <i class="user-icon icon-excel" />
            <div class="file-text">
              <bk-overflow-title
                class="text-overflow">
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
            <span>{{ $t('支持 Excel 文件，文件小于 10 M，下载') }}</span>
            <bk-button text theme="primary" @click="handleExportTemplate">{{ $t('模版文件') }}</bk-button>
          </div>
        </template>
      </bk-upload>
      <template #footer>
        <div class="footer-wrapper">
          <div class="footer-left">
            <bk-checkbox v-model="uploadInfo.overwrite">
              {{ $t('允许对同名用户覆盖更新') }}
            </bk-checkbox>
            <bk-popover
              ext-cls="popover-wrapper"
              :content="$t('针对相同用户覆盖更新相应的字段值，包括所属部门、所属上级等')"
              placement="top"
              width="280"
            >
              <InfoLine class="info" />
            </bk-popover>
          </div>
          <div>
            <bk-button
              theme="primary"
              class="w-[64px] mr-[8px]"
              :loading="importConfig.loading"
              @click="confirmImportUsers">
              {{ $t('导入') }}
            </bk-button>
            <bk-button
              class="w-[64px]"
              @click="closed">
              {{ $t('取消') }}
            </bk-button>
          </div>
        </div>
      </template>
    </bk-dialog>
</template>

<script setup lang="ts">
  import axios from 'axios';
  import router from '@/router';
  import Cookies from 'js-cookie';
  import { ref, reactive } from 'vue';
  import { t } from '@/language/index';
  import useAppStore from '@/store/app';
  import { InfoLine } from 'bkui-vue/lib/icon';
  import { InfoBox, Message } from 'bkui-vue';
  const props = defineProps({
    isShow: {
      type: Boolean,
      default: false
    },
    currentDataSourceId: {
      type: Number
    }
  });
  const emit = defineEmits(['update:isShow', 'success', 'close']);
  const importConfig = reactive({
    loading: false,
    title: t('导入'),
    id: 'local',
  });
  const uploadRef = ref();
  const isHover = ref(false);
  const textTips = ref('');
  const isError = ref(false);
  const uploadInfo = reactive({
    file: {},
    overwrite: false,
    incremental: true,
  });
  const customRequest = (data) => {
    if (data.file.size > (10 * 1024 * 1024)) {
      isError.value = true;
      textTips.value = t('文件大小超出限制');
    } else {
      isError.value = false;
      textTips.value = t('上传成功');
    }
    uploadInfo.file = data.file;
  };
  const closed = () => {
    emit('update:isShow', false)
  }
  const exceed = () => {
    Message({ theme: 'error', message: t('最多上传1个文件，如需更新，请先删除已上传文件') });
  };
  const getSize = (value) => {
    const size = value / 1024;
    return `${parseFloat(size.toFixed(2))}KB`;
  };
  const handleUploadRemove = (file) => {
    uploadRef.value?.handleRemove(file);
    uploadInfo.file = {};
  };
  // 数据源导出模板
  const handleExportTemplate = () => {
    const url = `${window.AJAX_BASE_URL}/api/v1/web/data-sources/${props.currentDataSourceId}/operations/download_template/`;
    window.open(url);
  };
  // 导入用户
  const confirmImportUsers = async () => {
    if (!uploadInfo.file.name) {
      return Message({ theme: 'warning', message: t('请选择文件再上传') });
    }
    if (isError.value) {
      return Message({ theme: 'warning', message: t('文件大小超出限制，请重新上传') });
    };

    try {
      importConfig.loading = true;
      const formData = new FormData();
      formData.append('file', uploadInfo.file);
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRFToken': Cookies.get(window.CSRF_COOKIE_NAME),
          'x-requested-with': 'XMLHttpRequest',
        },
        withCredentials: true,
      };
      const url = `${window.AJAX_BASE_URL}/api/v1/web/data-sources/${props.currentDataSourceId}/operations/import/`;
      const res = await axios.post(url, formData, config);
      if (res.data.data.status === 'success') {
        emit('update:isShow', false);
        InfoBox({
          infoType: 'success',
          title: t('导入成功'),
          confirmText: t('查看组织架构'),
          cancelText: t('关闭'),
          onConfirm: () => {
            emit('success');
          },
          onClosed: () => {
            emit('close')
          },
        });
      } else {
        Message({ theme: 'error', message: res.data.data.summary });
      }
    } catch (e) {
      Message({ theme: 'error', message: e.response.data.error.message });
    } finally {
      importConfig.loading = false;
    }
  };
</script>
<style lang="less" scoped>
.excel-file {
  display: flex;
  padding: 10px;
  overflow: hidden;
  font-size: 12px;
  flex: 1;
  align-items: center;

  .icon-excel {
    margin-right: 14px;
    font-size: 26px;
    color: #2dcb56;
  }

  .file-text {
    flex: 1;
    overflow: hidden;
  }

  .file-status {
    color: #2dcb56;
  }

  .file-operations {
    span {
      font-weight: 700;
    }

    .icon-delete {
      margin-left: 12px;
      font-size: 16px;
      cursor: pointer;
    }
  }
}
.footer-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;

  .footer-left {
    display: flex;
    align-items: center;
  }

  .info {
    margin-left: 5px;
    font-size: 16px;
    color: #979BA5;
    cursor: pointer;
  }
}
</style>
  