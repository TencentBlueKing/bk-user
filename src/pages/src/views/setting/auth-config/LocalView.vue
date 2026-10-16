<template>
  <div v-bkloading="{ loading: isLoading, zIndex: 10 }" class="details-info-wrapper">
    <ViewRow :title="$t('基础信息')">
      <LabelContent :label="$t('名称')">{{ idpsName }}</LabelContent>
      <LabelContent :label="$t('是否启用')">
        {{ idpsStatus ? $t('是') : $t('否') }}
      </LabelContent>
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
import { getLocalIdps } from '@/http';

interface IProps {
  idpId: string;
}

const props = defineProps<IProps>();

const emit = defineEmits(['detail-loaded']);

const isLoading = ref(false);
const scopeIds = ref([]);
const idpsName = ref({});
const idpsStatus = ref(true);

onMounted(async () => {
  try {
    isLoading.value = true;
    const data = (await getLocalIdps(props.idpId))?.data;
    idpsName.value = data?.name;
    idpsStatus.value = data?.plugin_config?.enable_password;
    scopeIds.value = data?.data_source_ids || [];
    emit('detail-loaded', data);
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
