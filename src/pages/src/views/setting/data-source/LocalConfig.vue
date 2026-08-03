<template>
  <bk-loading
    :loading="submitLoading"
    class="data-source-content user-scroll-y"
    :z-index="10"
  >
    <bk-form
      ref="formRef"
      :model="formModel"
      :rules="conflictRules"
      form-type="vertical"
    >
      <DataSourceBasicInfo
        v-model="formModel.name"
      />
      <Row :title="$t('导入')" class="!shadow-none !border-b-0">
        <div class="mb-[16px] w-[560px]">
          <ConflictTips
            type="alert"
            :has-other-data-source="hasOtherDataSource"
          />
          <ConflictConfig
            ref="conflictConfigRef"
            variant="dialog"
            :config="conflictConfig"
            class="mt-[16px]"
          />
        </div>
        <ExcelUpload v-model="uploadFile" class="w-[560px]" />
        <div class="btn mt-[16px]">
          <bk-button
            theme="primary"
            class="mr8"
            :loading="submitLoading"
            @click="handleSubmit"
          >
            {{ $t('提交') }}
          </bk-button>
          <bk-button @click="emit('cancel')">
            {{ $t('取消') }}
          </bk-button>
        </div>
      </Row>
    </bk-form>
  </bk-loading>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, ref } from 'vue';

import ConflictConfig from '@/components/conflict-config/ConflictConfig.vue';
import ConflictTips from '@/components/conflict-config/ConflictTips.vue';
import DataSourceBasicInfo from '@/components/DataSourceBasicInfo.vue';
import { UPLOAD_FILE_MAX_SIZE_BYTE } from '@/components/import-dialog/constants';
import ExcelUpload from '@/components/import-dialog/ExcelUpload.vue';
import Row from '@/components/layouts/ItemRow.vue';
import { useConflictRules } from '@/hooks/useConflictRules';
import { useDataSourceImport } from '@/hooks/useDataSourceImport';
import { getDefaultConfig, newDataSource } from '@/http/dataSourceFiles';
import { UsernameGenerateConfig } from '@/http/types/dataSourceFiles';
import { t } from '@/language/index';
import { useDataSourceStore } from '@/store';

interface Props {
  dataSourceId: number | null;
}

defineProps<Props>();
const emit = defineEmits<{
  cancel: [];
  updateSuccess: [payload: { text: string; dataSourceId: number; name: string }];
}>();

const conflictConfigRef = ref();
const conflictConfig = ref<UsernameGenerateConfig>({
  rule: 'unchanged',
  prefix: '',
  suffix: '',
});
const { rules: conflictRules } = useConflictRules(conflictConfigRef);
const formRef = ref();
const formModel = ref<{ name?: string }>({ name: '' });
const uploadFile = ref<File | null>(null);
const dataSourceStore = useDataSourceStore();
const hasOtherDataSource = computed(() => dataSourceStore.dataSource.length > 0);
const { uploadImport } = useDataSourceImport();
const submitLoading = ref(false);

const handleSubmit = async () => {
  try {
    const valid = await formRef.value?.validate().catch(() => false);
    if (!valid) return;
    if (!uploadFile.value) {
      Message({ theme: 'warning', message: t('请选择文件再上传') });
      return;
    }
    if (uploadFile.value.size > UPLOAD_FILE_MAX_SIZE_BYTE) {
      Message({ theme: 'warning', message: t('文件大小超出限制') });
      return;
    }

    submitLoading.value = true;
    const res = await getDefaultConfig('local');
    const result = await newDataSource({
      plugin_id: 'local',
      name: formModel.value.name,
      plugin_config: {
        ...res.data?.config,
      },
      username_generate_config: conflictConfigRef.value?.getData(),
    });

    const dataSourceId = result.data?.id;
    if (!dataSourceId) {
      Message({ theme: 'error', message: t('创建数据源失败') });
      return;
    }

    await uploadImport(dataSourceId, uploadFile.value);
    window.changeInput = false;
    emit('updateSuccess', {
      text: t('新建成功'),
      dataSourceId,
      name: formModel.value.name,
    });
  } catch (e) {
    console.error(e);
    // 透传后端错误信息（如名称重复等），避免统一提示掩盖具体原因
    const errorMessage = (e as { response?: { data?: { error?: { message?: string } } } })
      ?.response?.data?.error?.message;
    Message({ theme: 'error', message: errorMessage || t('操作失败') });
  } finally {
    submitLoading.value = false;
  }
};
</script>
