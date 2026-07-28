<template>
  <bk-dialog
    :is-show="isShow"
    :quick-close="false"
    :width="640"
    @closed="closed"
  >
    <template #header>
      <span class="text-[#313238] text-[20px]">
        {{ $t('导入') }}
      </span>
    </template>
    <bk-loading :loading="importLoading || isDataSourceSyncing">
      <template v-if="isFirstlyImport">
        <ConflictTips
          type="alert"
          :has-other-data-source="!dataSourceStore.isConfiguredOtherPlugin"
        />
        <bk-form
          ref="formRef"
          :model="formModel"
          :rules="conflictRules"
          form-type="vertical"
          class="mt-[16px]"
        >
          <ConflictConfig
            ref="conflictConfigRef"
            variant="dialog"
            :config="conflictConfig"
            class="mb-[16px]"
          />
        </bk-form>
      </template>
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
    </bk-loading>
    <template #footer>
      <div class="footer-wrapper">
        <div class="footer-left">
          <template v-if="!isFirstlyImport">
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
          </template>
        </div>
        <div>
          <bk-button
            theme="primary"
            class="w-[64px] mr-[8px]"
            :disabled="importLoading || isDataSourceSyncing"
            @click="handleConfirm">
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
import { InfoBox, Message } from 'bkui-vue';
import { InfoLine } from 'bkui-vue/lib/icon';
import Cookies from 'js-cookie';
import { computed, reactive, ref } from 'vue';

import ConflictConfig from '../conflict-config/ConflictConfig.vue';
import ConflictTips from '../conflict-config/ConflictTips.vue';

import { isNil } from '@/common/util';
import { useConflictRules } from '@/hooks/useConflictRules';
import useDataSourceSetting from '@/hooks/useDataSourceSetting';
import { getDefaultConfig, newDataSource } from '@/http/dataSourceFiles';
import { UsernameGenerateConfig } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';
import { useDataSourceStore } from '@/store';

interface IProps {
  dataSourceId?: number;
}
const isShow = defineModel<boolean>('isShow');
const props = defineProps<IProps>();
const emit = defineEmits(['success']);

const dataSourceStore = useDataSourceStore();

const conflictConfigRef = ref();
const { rules: conflictRules } = useConflictRules(conflictConfigRef);
const conflictConfig = ref<UsernameGenerateConfig>({
  rule: 'unchanged',
  prefix: '',
  suffix: '',
});

/** 这里无实际意义，但为了配合form校验，得有一个model */
const formModel = ref({});

const currentLocalDataSourceId = ref(props.dataSourceId);
const importLoading = ref(false);
const uploadRef = ref();
const isHover = ref(false);
const textTips = ref('');
const isError = ref(false);
const uploadInfo = reactive({
  file: {},
  overwrite: false,
  incremental: true,
});
const formRef = ref();

const isFirstlyImport = computed(() => isNil(props.dataSourceId));

/** 本地数据源插件 - 数据同步状态 */
// eslint-disable-next-line max-len
const localDataSourceStatus = computed(() => dataSourceStore.dataSourceSyncStatusMap.get(currentLocalDataSourceId.value)?.status);

/** 本地数据源是否同步中 */
const isDataSourceSyncing = computed(() => dataSourceStore.isDataSourceSyncing(localDataSourceStatus.value));


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

/** 关闭弹窗 */
const closed = () => {
  uploadInfo.file = {};
  uploadInfo.overwrite = false;
  uploadInfo.incremental = true;
  isShow.value = false;
};
const exceed = () => {
  Message({ theme: 'error', message: t('最多上传1个文件，如需更新，请先删除已上传文件') });
};

const getSize = (value: number) => {
  const size = value / 1024;
  return `${parseFloat(size.toFixed(2))}KB`;
};

const handleUploadRemove = (file) => {
  uploadRef.value?.handleRemove(file);
  uploadInfo.file = {};
};

// 数据源导出模板
const handleExportTemplate = () => {
  const url = `${window.AJAX_BASE_URL}/api/v3/web/data-sources/operations/download_template/`;
  window.open(url);
};

/**
 * @description 首次导入本地数据源，需要先配置用户名冲突，创建dataSourceId后才可上传
 */
const handleConfirm = async () => {
  let allowUpload = true;
  if (isFirstlyImport.value) {
    allowUpload = await createDataSource();
  }
  if (!allowUpload) return;
  await confirmImportUsers();
};

/** 创建本地数据源 */
const createDataSource = async () => {
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;
  const res = await getDefaultConfig('local');
  const newDataSourceData = await newDataSource({
    plugin_id: 'local',
    plugin_config: {
      ...res.data?.config,
    },
    username_generate_config: conflictConfigRef.value.getData(),
  });
  currentLocalDataSourceId.value = newDataSourceData.data?.id;
  return Boolean(newDataSourceData.data?.id);
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
    importLoading.value = true;
    const formData = new FormData();
    formData.append('file', uploadInfo.file);
    formData.append('overwrite', uploadInfo.overwrite);
    if (conflictConfigRef.value) {
      const usernameConfig = conflictConfigRef.value.getData();
      formData.append('username_generate_config', JSON.stringify(usernameConfig));
    }
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': Cookies.get(window.CSRF_COOKIE_NAME),
        'x-requested-with': 'XMLHttpRequest',
      },
      withCredentials: true,
    };
    const url = `${window.AJAX_BASE_URL}/api/v3/web/data-sources/${currentLocalDataSourceId.value}/operations/import/`;
    const res = await axios.post(url, formData, config);
    // 确保 importLoading 在最终状态(success/failed/backend error) 下才停止loading
    // 因此取消在finally中处理loading的逻辑
    if (res.data.data.status === 'success') {
      importLoading.value = false;
      importSuccess();
    } else if (res.data.data.status === 'failed') {
      importLoading.value = false;
      Message({ theme: 'error', message: res.data.data.summary });
    } else {
      startDataSourceSync(currentLocalDataSourceId.value, 'local');
    }
  } catch (e) {
    importLoading.value = false;
    Message({ theme: 'error', message: e.response.data.error.message });
  }
};

/** 停止轮询时的钩子方法 [获取导入本地数据源状态] */
const afterSyncImportData = () => {
  importLoading.value = false;
  if (localDataSourceStatus.value === 'success') {
    importSuccess();
  } else if (localDataSourceStatus.value === 'failed') {
    Message({ theme: 'error', message: t('同步失败') });
  }
};

const { startDataSourceSync } = useDataSourceSetting(afterSyncImportData);

/** 导入成功时执行 */
const importSuccess = () => {
  isShow.value = false;
  InfoBox({
    infoType: 'success',
    title: t('导入成功'),
    confirmText: t('查看组织架构'),
    onConfirm: () => {
      emit('success');
    },
  });
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
