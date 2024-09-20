<template>
  <div class="view-details-wrapper">
    <ViewRow :title="$t('基本信息')">
      <div class="w-[480px]">
        <LabelContent :label="$t('租户名称')">{{ tenantsData.name }}</LabelContent>
        <LabelContent :label="$t('租户ID')">{{ tenantsData.id }}</LabelContent>
        <LabelContent :label="$t('状态')">
          <bk-tag :theme="tenantsData.status === 'enabled' ? 'success' : ''">
            {{ tenantStatus[tenantsData.status]?.text }}
          </bk-tag>
        </LabelContent>
      </div>
      <img v-if="tenantsData.logo" class="user-logo" :src="tenantsData.logo" alt="">
      <i v-else class="user-icon icon-yonghu" />
    </ViewRow>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import ViewRow from '@/components/layouts/ViewRow.vue';
import { tenantStatus } from '@/utils';

defineProps({
  tenantsData: {
    type: Object,
    default: {},
  },
});
</script>

<style lang="less" scoped>
.view-details-wrapper {
  position: relative;
  padding: 24px 40px;

  .user-logo, .user-icon {
    position: absolute;
    top: 53px;
    right: 40px;
    width: 72px;
    height: 72px;
    border: 1px dashed #c4c6cc;
    object-fit: contain;
  }

  .icon-yonghu {
    margin-right: 0;
    font-size: 40px;
    line-height: 72px;
    color: #DCDEE5;
    background: #FAFBFD;
  }
}
</style>
