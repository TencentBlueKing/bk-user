<template>
  <div class="w-full pt-[16px] bg-[#fff]">
    <bk-form form-type="vertical">
      <Row :title="$t('文件导入')">
        <div class="px-[40px]">
          <bk-alert v-if="showCreatedTip" theme="success" class="mb-[16px]">
            <span>{{ $t('数据源「x」已创建，导入或跳过都不影响该数据源', { name: dataSourceName }) }}</span>
          </bk-alert>
          <bk-form-item>
            <ExcelUpload v-model="uploadFile" />
            <!-- 失败原因内联展示在文件卡片下方：裸 axios 不经统一错误拦截，需自行透传后端原因 -->
            <bk-alert v-if="failReason" theme="error" class="mt-[8px]">
              <span>{{ failReason }}</span>
            </bk-alert>
            <!-- 编辑导入页签导入成功后停留在当前页，与失败态对称内联展示成功提示 -->
            <bk-alert v-if="importSuccess" theme="success" class="mt-[8px]">
              <span>{{ $t('导入成功') }}</span>
            </bk-alert>
          </bk-form-item>
        </div>
      </Row>
    </bk-form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

import ExcelUpload from '@/components/import-dialog/ExcelUpload.vue';
import Row from '@/components/layouts/ItemRow.vue';
import { useDataSourceImport } from '@/hooks/useDataSourceImport';
import { t } from '@/language/index';

interface Props {
  /** 待导入的数据源 id，为空时无法导入 */
  dataSourceId: number | null;
  /** 数据源名称，用于「已创建」提示文案 */
  dataSourceName?: string;
  /** 创建向导第 2 步展示「数据源已创建」提示，编辑导入页签不展示 */
  showCreatedTip?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  dataSourceName: '',
  showCreatedTip: false,
});

const emit = defineEmits<{
  /** 文件选中状态变化：容器据此禁用「导入并继续」按钮 */
  fileChange: [hasFile: boolean];
}>();

const { uploadImport } = useDataSourceImport();

const uploadFile = ref<File | null>(null);
const failReason = ref('');
const importSuccess = ref(false);

watch(uploadFile, file => emit('fileChange', Boolean(file)), { immediate: true });

/**
 * 上传并导入：失败时透传后端原因（裸 axios 不经统一拦截），停留在当前步骤可重试
 * @returns 是否导入成功，按钮态与步骤流转由容器根据返回值驱动
 */
const handleImport = async () => {
  if (!props.dataSourceId) return false;
  if (!uploadFile.value) {
    failReason.value = t('请选择文件再上传');
    return false;
  }
  failReason.value = '';
  importSuccess.value = false;
  try {
    const res = await uploadImport(props.dataSourceId, uploadFile.value);
    // 接口 HTTP 200 但业务失败（如 Excel 内容错误）也需按失败处理，否则会误报成功
    if (res.data.data.status === 'failed') {
      failReason.value = res.data.data.summary || t('操作失败');
      return false;
    }
    importSuccess.value = true;
    return true;
  } catch (e) {
    console.error(e);
    const errorMessage = (e as { response?: { data?: { error?: { message?: string } } } })
      ?.response?.data?.error?.message;
    failReason.value = errorMessage || t('操作失败');
    return false;
  }
};

defineExpose({
  importFile: handleImport,
});
</script>
