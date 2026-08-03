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
      <ExcelUpload v-model="uploadInfo.file" @exceed="handleExceed" />
    </bk-loading>
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
      </div>
      <div>
        <bk-button
          theme="primary"
          class="w-[64px] mr-[8px]"
          :disabled="importLoading || isDataSourceSyncing"
          @click="confirmImportUsers">
          {{ $t('导入') }}
        </bk-button>
        <bk-button
          class="w-[64px]"
          @click="closed">
          {{ $t('取消') }}
        </bk-button>
      </div>
    </template>
  </bk-dialog>
</template>

<script setup lang="ts">
import { InfoBox, Message } from 'bkui-vue';
import { InfoLine } from 'bkui-vue/lib/icon';
import { computed, reactive, ref } from 'vue';

import { UPLOAD_FILE_MAX_SIZE_BYTE } from '@/components/import-dialog/constants';
import ExcelUpload from '@/components/import-dialog/ExcelUpload.vue';
import { useDataSourceImport } from '@/hooks/useDataSourceImport';
import useDataSourceSetting from '@/hooks/useDataSourceSetting';
import { t } from '@/language/index';
import { useDataSourceStore } from '@/store';

interface IProps {
  dataSourceId?: number;
}
const isShow = defineModel<boolean>('isShow');
const props = defineProps<IProps>();
const emit = defineEmits(['success']);

const dataSourceStore = useDataSourceStore();

const currentLocalDataSourceId = ref(props.dataSourceId);
const importLoading = ref(false);
const uploadInfo = reactive({
  file: null as File | null,
  overwrite: false,
  incremental: true,
});
/** 本地数据源插件 - 数据同步状态 */
// eslint-disable-next-line max-len
const localDataSourceStatus = computed(() => dataSourceStore.dataSourceSyncStatusMap.get(currentLocalDataSourceId.value)?.status);

/** 本地数据源是否同步中 */
const isDataSourceSyncing = computed(() => dataSourceStore.isDataSourceSyncing(localDataSourceStatus.value));

/** 关闭弹窗 */
const closed = () => {
  uploadInfo.file = null;
  uploadInfo.overwrite = false;
  uploadInfo.incremental = true;
  isShow.value = false;
};
const handleExceed = () => {
  Message({ theme: 'error', message: t('最多上传1个文件，如需更新，请先删除已上传文件') });
};

// 导入用户
const confirmImportUsers = async () => {
  if (!uploadInfo.file) {
    return Message({ theme: 'warning', message: t('请选择文件再上传') });
  }
  if (uploadInfo.file.size > UPLOAD_FILE_MAX_SIZE_BYTE) {
    return Message({ theme: 'warning', message: t('文件大小超出限制') });
  };

  try {
    importLoading.value = true;
    const res = await uploadImport(currentLocalDataSourceId.value, uploadInfo.file, uploadInfo.overwrite);
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

const { uploadImport } = useDataSourceImport();
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
