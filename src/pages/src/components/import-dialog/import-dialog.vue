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
import { useDataSourceImportTask } from '@/hooks/useDataSourceImportTask';
import { t } from '@/language/index';
import { useDataSourceStore } from '@/store';

interface IProps {
  dataSourceId?: number;
}
const isShow = defineModel<boolean>('isShow');
const props = defineProps<IProps>();
const emit = defineEmits(['success']);

const dataSourceStore = useDataSourceStore();

const importLoading = ref(false);
const uploadInfo = reactive({
  file: null as File | null,
  overwrite: false,
  incremental: true,
});
/** 本地数据源插件 - 数据同步状态 */
// eslint-disable-next-line max-len
const localDataSourceStatus = computed(() => dataSourceStore.dataSourceSyncStatusMap.get(props.dataSourceId)?.status);

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
    // 异步任务：importTask 在任务出最终结果后才兑现，loading 由轮询期间的同步状态共同驱动
    const { success, summary } = await importTask(props.dataSourceId, uploadInfo.file, uploadInfo.overwrite);
    importLoading.value = false;
    if (success) {
      importSuccess();
    } else {
      Message({ theme: 'error', message: summary || t('同步失败') });
    }
  } catch (e) {
    importLoading.value = false;
    Message({ theme: 'error', message: e.response.data.error.message });
  }
};

const { importTask } = useDataSourceImportTask();

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
