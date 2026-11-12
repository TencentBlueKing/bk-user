import { computed, ref } from 'vue';

import { getFields } from '@/http';
import { t } from '@/language/index';

/**
 * 内置/自定义字段下拉选项，数据源 ↔ 认证源匹配各场景共用：
 * refs 由调用方拉取 getFields 后填充，或直接调用 loadFields
 */
export function useIdpFields() {
  const builtinFields = ref([]);
  const customFields = ref([]);

  const fieldOptions = computed(() => [
    ...(builtinFields.value as Array<{ id: number; name: string }>).map(item => ({ key: item.id, name: item.name, type: t('内置') })),
    ...(customFields.value as Array<{ id: number; name: string }>).map(item => ({ key: item.id, name: item.name, type: t('自定义') })),
  ]);

  const loadFields = async () => {
    const fieldRes = await getFields();
    builtinFields.value = fieldRes.data?.builtin_fields || [];
    customFields.value = fieldRes.data?.custom_fields || [];
  };

  return {
    builtinFields,
    customFields,
    fieldOptions,
    loadFields,
  };
}
