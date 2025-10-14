<template>
  <div class="py-[37px] px-[55px]">
    <LabelContent :label="$t('账号ID')">{{ detailsInfo?.id }}</LabelContent>
    <LabelContent :label="$t('用户名')">{{ detailsInfo?.username }}</LabelContent>
    <LabelContent :label="$t('全名')">{{ detailsInfo?.full_name }}</LabelContent>
    <LabelContent :label="$t('所属应用')">
      <span>{{ detailsInfo?.app_codes }}</span>
    </LabelContent>
    <LabelContent :label="$t('账号责任人')">
      <DisplayName :user-id="detailsInfo?.owners" />
    </LabelContent>
  </div>
</template>

<script lang="ts" setup>
import DisplayName from '@/components/display-name.vue';
import LabelContent from '@/components/layouts/LabelContent.vue';
defineProps({
  detailsInfo: {
    type: Object,
    default: {},
  },
});
</script>
