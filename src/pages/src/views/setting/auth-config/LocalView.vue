<template>
  <div v-bkloading="{ loading: isLoading, zIndex: 10 }" class="details-info-wrapper">
    <ViewRow :title="$t('基础信息')">
      <LabelContent :label="$t('名称')">{{ authSourceData?.name }}</LabelContent>
      <LabelContent :label="$t('是否启用')">{{ authSourceData?.status === 'enabled' ? $t('是') : $t('否') }}</LabelContent>
      <LabelContent :label="$t('生效范围')">
        <EffectiveScopeView :source-ids="scopeIds" />
      </LabelContent>
    </ViewRow>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

import EffectiveScopeView from './EffectiveScopeView.vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import ViewRow from '@/components/layouts/ViewRow.vue';
import { getIdpsDetails } from '@/http';
import type { IdpDetail } from '@/http/types/authSourceFiles';

interface IProps {
  idpId: string;
}

const props = defineProps<IProps>();

const emit = defineEmits(['detail-loaded']);

const isLoading = ref(false);
const authSourceData = ref<IdpDetail>();
const scopeIds = ref<number[]>([]);

onMounted(async () => {
  try {
    isLoading.value = true;
    authSourceData.value = (await getIdpsDetails(props.idpId))?.data;
    // 生效范围从通用详情的匹配规则反推，field_compare_rules 由后端固定为 id 对 id，展示不需要
    scopeIds.value = authSourceData.value?.data_source_match_rules?.map(item => item.data_source_id) || [];
    emit('detail-loaded', authSourceData.value);
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style lang="less" scoped>
.details-info-wrapper {
  padding: 28px 40px;

  .row-wrapper {
    padding-bottom: 24px;
    border-bottom: 1px solid #EAEBF0;

    &:last-child {
      border-bottom: none !important;
    }
  }
}
</style>
