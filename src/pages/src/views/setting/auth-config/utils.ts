import { DataSourceMatchRule } from '@/http/types/authSourceFiles';

/**
 * 阶段适配：将一份 field_compare_rules 按生效范围 data_source_id 逐个复制拼入 data_source_match_rules。
 * 后端完成 1:N 改造后，此函数可直接删除。
 *
 * @param fieldCompareRules - 登录认证匹配中配置的字段比对规则
 * @param dataSourceIds     - 生效范围选中的数据源 ID 列表
 * @returns 每个 data_source_id 各挂一份 field_compare_rules 的 DataSourceMatchRule 数组
 */
export function buildDataSourceMatchRules(
  fieldCompareRules: { source_field: string; target_field: string }[],
  dataSourceIds: number[],
): DataSourceMatchRule[] {
  return dataSourceIds.map(id => ({
    data_source_id: id,
    field_compare_rules: fieldCompareRules,
  }));
}
