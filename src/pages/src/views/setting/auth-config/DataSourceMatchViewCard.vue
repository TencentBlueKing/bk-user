<template>
  <div class="match-view-card">
    <div class="match-view-card-header">{{ dataSourceName }}</div>
    <Table :data="fieldCompareRules" :header-cell-style="{ color: '#979BA5' }">
      <TableColumn field="target_field" :label="$t('数据源字段')" show-overflow="tooltip" />
      <TableColumn field="source_field" :label="$t('认证源字段')" show-overflow="tooltip" />
    </Table>
  </div>
</template>

<script setup lang="ts">
import { Table, TableColumn } from '@blueking/table';

interface IProps {
  dataSourceName: string;
  fieldCompareRules: { target_field: string; source_field: string }[];
}

defineProps<IProps>();
</script>

<style lang="less" scoped>
.match-view-card {
  margin-bottom: 16px;
  border: 1px solid #DCDEE5;
  border-radius: 2px;
  overflow: hidden;

  .match-view-card-header {
    height: 32px;
    padding: 0 12px;
    background: #F0F1F5;
    font-size: 12px;
    font-weight: 400;
    line-height: 20px;
    display: flex;
    align-items: center;
    color: var(--title-color);
  }
}
</style>
