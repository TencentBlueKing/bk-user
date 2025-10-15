<template>
  <div class="py-[37px] px-[55px]">
    <LabelContent :label="$t('账号ID')">{{ detailsInfo?.id }}</LabelContent>
    <LabelContent :label="$t('用户名')">{{ detailsInfo?.username }}</LabelContent>
    <LabelContent :label="$t('全名')">{{ detailsInfo?.full_name }}</LabelContent>
    <LabelContent :label="$t('所属应用')">
      <span>{{ detailsInfo?.app_codes }}</span>
    </LabelContent>
    <LabelContent :label="$t('账号责任人')">
      <bk-user-display-name :user-id="detailsInfo?.owners"></bk-user-display-name>
    </LabelContent>
  </div>
</template>

<script lang="ts" setup>
import LabelContent from '@/components/layouts/LabelContent.vue';
defineProps({
  detailsInfo: {
    type: Object,
    default: {},
  },
});
</script>
