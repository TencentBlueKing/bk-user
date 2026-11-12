import { type ComputedRef, type Ref, ref, toRaw, watch } from 'vue';

import { useIdpFields } from './useIdpFields';

interface IMatchRule {
  data_source_id: number;
  field_compare_rules: { source_field: string; target_field: string }[];
}

/**
 * 登录认证匹配（数据源 ↔ 认证源映射）共享逻辑，供 WeCom / CustomLogin 等认证源编辑页复用：
 * 生效范围与匹配规则卡片的双向同步、目标字段下拉选项、未保存状态（isDisabled）判断。
 */
export function useDataSourceMatch<T extends { data_source_match_rules: IMatchRule[] }>(
  formData: Ref<T>,
  scopeIds: Ref<number[]>,
  /** 编辑态是否有认证源 id（未保存状态判断使用） */
  hasId: ComputedRef<boolean> | Ref<boolean>,
) {
  // 三份数据由调用方页面在 onMounted 中填充；dataSourceList 元素为 { key: 数据源 id, name, disabled }
  const dataSourceList = ref([]);
  const { builtinFields, customFields, fieldOptions } = useIdpFields();
  // 是否无未保存修改（编辑态保存按钮的 disabled 依据），创建态恒为可保存
  const isDisabled = ref(true);

  // 编辑态初始快照，仅记录一次；与当前值序列化比对得出未保存状态
  let originalData: Record<string, unknown> = {};
  let originalScope: number[] = [];

  /** 记录初始快照，供未保存状态比对（页面数据回填完成后调用） */
  const markOriginalSnapshot = () => {
    originalData = JSON.parse(JSON.stringify(toRaw(formData.value)));
    originalScope = [...scopeIds.value];
  };

  /** 卡片关闭 = 取消勾选该数据源的生效范围，规则数组由下方 watch 自动收敛 */
  const handleRemoveCard = (id: number) => {
    scopeIds.value = scopeIds.value.filter(val => val !== id);
  };

  const getDataSourceName = (id: number) => (
    (dataSourceList.value as Array<{ key: number; name: string }>).find(item => item.key === id)?.name || ''
  );

  // 未保存状态判断：无现成 deep-equal 工具，走序列化快照比对；toRaw 剥离响应式代理后再比对
  watch(formData, () => {
    isDisabled.value = hasId.value
      ? JSON.stringify(originalData) === JSON.stringify(toRaw(formData.value))
        && JSON.stringify(scopeIds.value) === JSON.stringify(originalScope)
      : false;
  }, { deep: true });

  // 生效范围由用户直接操作（勾选/卡片关闭），变动即视为已修改，不等 formData 联动后的比对结果
  watch(scopeIds, () => {
    isDisabled.value = false;
  }, { deep: true });

  // 生效范围与登录认证匹配卡片双向同步：选中即生成对应卡片，取消选择/卡片关闭即移除规则
  watch(scopeIds, (ids) => {
    const selected = new Set(ids);
    formData.value.data_source_match_rules = formData.value.data_source_match_rules
      .filter(rule => selected.has(rule.data_source_id));
    ids.forEach((id) => {
      if (!formData.value.data_source_match_rules.some(rule => rule.data_source_id === id)) {
        formData.value.data_source_match_rules.push({
          data_source_id: id,
          field_compare_rules: [{ target_field: '', source_field: '' }],
        });
      }
    });
  }, { immediate: true, deep: true });

  return {
    dataSourceList,
    builtinFields,
    customFields,
    fieldOptions,
    isDisabled,
    markOriginalSnapshot,
    handleRemoveCard,
    getDataSourceName,
  };
}
